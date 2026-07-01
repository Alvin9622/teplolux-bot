import { Inject, Injectable, LoggerService } from '@nestjs/common';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { LogEvent } from '../../../logger/log-events';
import { I18nService } from '../../../i18n/i18n.service';
import { TKey } from '../../../i18n/i18n.keys';
import { Locale } from '../../../i18n/i18n.types';
import { escapeHtml } from '../constants/messages.constants';
import { Keyboards } from '../keyboards/main-menu.keyboard';
import { HandlerContext } from '../handlers/handler-context';
import { TelegramResponderService } from '../services/telegram-responder.service';
import { ConversationStateStore } from './conversation-state.store';
import { FlowRegistry } from './flow.registry';
import { FlowKeyboards, StepControlOptions } from './flow.keyboards';
import { FLOW_TRIGGERS, FlowAction } from './conversation.constants';
import { ConversationState, FlowDefinition, FlowStep } from './conversation.types';

/**
 * Generic guided-conversation engine.
 *
 * Drives ANY registered {@link FlowDefinition}: it asks each step's question,
 * validates the answer, supports ⬅ Back / ❌ Cancel at every step, shows a
 * confirmation summary with Confirm / Edit / Cancel, and keeps all collected
 * data in transient Redis state. It is flow-agnostic — no specific flow is
 * hardcoded — so future flows reuse it as-is.
 */
@Injectable()
export class ConversationService {
  constructor(
    private readonly store: ConversationStateStore,
    private readonly flows: FlowRegistry,
    private readonly responder: TelegramResponderService,
    private readonly i18n: I18nService,
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
  ) {}

  /** True when the user currently has an active flow. */
  async isActive(telegramId: bigint | number): Promise<boolean> {
    return (await this.store.get(telegramId)) !== null;
  }

  /** Silently drop any active flow (used when a command interrupts the flow). */
  async abort(telegramId: bigint | number): Promise<void> {
    await this.store.clear(telegramId);
  }

  // -------------------------------------------------------------------------
  // Callback handling (menu triggers + flow controls)
  // -------------------------------------------------------------------------

  /** Returns true when the callback started or advanced a flow. */
  async handleCallback(context: HandlerContext, data: string): Promise<boolean> {
    const trigger = FLOW_TRIGGERS[data];
    if (trigger) {
      await this.start(context, trigger.flowId, trigger.topic, trigger.subject);
      return true;
    }

    const loaded = await this.load(context);
    if (!loaded) {
      return false;
    }
    const { state, flow } = loaded;

    if (data === FlowAction.Cancel) {
      await this.cancel(context);
      return true;
    }

    if (data === FlowAction.Back) {
      await this.goBack(context, state, flow);
      return true;
    }

    if (data === FlowAction.Submit) {
      if (state.mode === 'summary') {
        await this.submit(context, state, flow);
      }
      return true;
    }

    if (data === FlowAction.Edit) {
      await this.responder.sendText(
        context,
        this.i18n.t(context.locale, TKey.flowEditChoose),
        FlowKeyboards.editChoose(this.i18n.scoped(context.locale), flow),
      );
      return true;
    }

    if (data.startsWith(FlowAction.EditFieldPrefix)) {
      const stepId = data.slice(FlowAction.EditFieldPrefix.length);
      const step = this.stepById(flow, stepId);
      if (step) {
        state.mode = 'edit';
        state.editStepId = stepId;
        await this.store.set(context.user.telegramId, state);
        await this.renderStep(context, state, step);
      }
      return true;
    }

    if (data === FlowAction.Skip) {
      const step = this.currentStep(state, flow);
      if (step?.optional) {
        await this.acceptValue(context, state, flow, step, '');
      }
      return true;
    }

    if (data.startsWith(FlowAction.ChoicePrefix)) {
      const step = this.currentStep(state, flow);
      const value = data.slice(FlowAction.ChoicePrefix.length);
      if (step?.type === 'choice' && (step.choices ?? []).some((c) => c.value === value)) {
        await this.acceptValue(context, state, flow, step, value);
      }
      return true;
    }

    return false;
  }

  // -------------------------------------------------------------------------
  // Message handling (step answers)
  // -------------------------------------------------------------------------

  /** Returns true when the message was consumed by an active flow. */
  async handleMessage(context: HandlerContext): Promise<boolean> {
    const loaded = await this.load(context);
    if (!loaded) {
      return false;
    }
    const { state, flow } = loaded;
    const text = context.message?.text?.trim();

    // Reply-keyboard "Cancel"/"Back" buttons send localized text.
    if (text && this.matches(text, TKey.flowButtonCancel)) {
      await this.cancel(context);
      return true;
    }
    if (text && this.matches(text, TKey.flowButtonBack)) {
      await this.goBack(context, state, flow);
      return true;
    }

    // In summary mode we expect button presses; gently re-show the summary.
    if (state.mode === 'summary') {
      await this.renderSummary(context, state, flow);
      return true;
    }

    const step = this.currentStep(state, flow);
    if (!step) {
      return true;
    }

    // Shared contact (phone step) or shared location (location step).
    const sharedPhone = context.message?.contact?.phone_number;
    if (step.type === 'phone' && sharedPhone) {
      await this.acceptValue(context, state, flow, step, sharedPhone);
      return true;
    }
    const sharedLocation = context.message?.location;
    if (step.type === 'location' && sharedLocation) {
      await this.acceptValue(
        context,
        state,
        flow,
        step,
        `${sharedLocation.latitude},${sharedLocation.longitude}`,
      );
      return true;
    }

    // Choice steps are answered via inline buttons only — re-prompt on text.
    if (step.type === 'choice' || text === undefined || text.length === 0) {
      await this.renderStep(context, state, step);
      return true;
    }

    const result = step.validate(text);
    if (!result.ok) {
      this.logger.warn(
        `${LogEvent.FlowValidationFailed}: ${flow.id}.${step.id}`,
        ConversationService.name,
      );
      await this.responder.sendText(context, this.i18n.t(context.locale, result.errorKey));
      await this.renderStep(context, state, step);
      return true;
    }

    await this.acceptValue(context, state, flow, step, result.value);
    return true;
  }

  // -------------------------------------------------------------------------
  // Lifecycle
  // -------------------------------------------------------------------------

  private async start(
    context: HandlerContext,
    flowId: string,
    topic: string,
    subject?: string,
  ): Promise<void> {
    const flow = this.flows.get(flowId);
    if (!flow || flow.steps.length === 0) {
      return;
    }
    const state: ConversationState = {
      flowId,
      topic,
      subject,
      currentStepId: flow.steps[0].id,
      history: [],
      mode: 'collect',
      data: {},
    };
    await this.store.set(context.user.telegramId, state);
    this.logger.log(
      `${LogEvent.FlowStarted}: ${flowId} topic=${topic}${subject ? `/${subject}` : ''}`,
      ConversationService.name,
    );

    await this.responder.sendText(
      context,
      this.i18n.t(context.locale, TKey.flowStarted, {
        topic: this.i18n.t(context.locale, flow.topicLabelKey(topic)),
      }),
    );
    await this.renderStep(context, state, flow.steps[0]);
  }

  /** Persist an accepted value and advance the flow (or return to the summary). */
  private async acceptValue(
    context: HandlerContext,
    state: ConversationState,
    flow: FlowDefinition,
    step: FlowStep,
    value: string,
  ): Promise<void> {
    state.data[step.id] = value;
    this.logger.log(
      `${LogEvent.FlowStepCompleted}: ${flow.id}.${step.id}`,
      ConversationService.name,
    );

    // Leaving a reply-keyboard step (phone/location) clears its custom keyboard.
    if (this.usesReplyKeyboard(step)) {
      await this.responder.removeReplyKeyboard(context, '✅');
    }

    if (state.mode === 'edit') {
      state.mode = 'summary';
      delete state.editStepId;
      await this.store.set(context.user.telegramId, state);
      await this.renderSummary(context, state, flow);
      return;
    }

    const nextStep = this.nextStep(flow, step);
    if (nextStep) {
      state.history.push(step.id);
      state.currentStepId = nextStep.id;
      await this.store.set(context.user.telegramId, state);
      await this.renderStep(context, state, nextStep);
      return;
    }

    state.mode = 'summary';
    await this.store.set(context.user.telegramId, state);
    await this.renderSummary(context, state, flow);
  }

  /** ⬅ Back: return to the previous step (or the summary when editing). */
  private async goBack(
    context: HandlerContext,
    state: ConversationState,
    flow: FlowDefinition,
  ): Promise<void> {
    const leaving = this.currentStep(state, flow);
    if (leaving && this.usesReplyKeyboard(leaving)) {
      await this.responder.removeReplyKeyboard(context, '↩️');
    }

    if (state.mode === 'edit') {
      state.mode = 'summary';
      delete state.editStepId;
      await this.store.set(context.user.telegramId, state);
      await this.renderSummary(context, state, flow);
      return;
    }

    const previousId = state.history.pop();
    if (!previousId) {
      // Back from the first step behaves like cancel → main menu.
      await this.cancel(context);
      return;
    }
    const previousStep = this.stepById(flow, previousId);
    if (!previousStep) {
      await this.cancel(context);
      return;
    }
    state.currentStepId = previousId;
    await this.store.set(context.user.telegramId, state);
    await this.renderStep(context, state, previousStep);
  }

  /** Cancel the active flow (also used by the `/cancel` command). */
  async cancel(context: HandlerContext): Promise<void> {
    await this.store.clear(context.user.telegramId);
    this.logger.log(LogEvent.FlowCancelled, ConversationService.name);
    // removeReplyKeyboard in case a phone/location reply keyboard is still shown.
    await this.responder.removeReplyKeyboard(
      context,
      this.i18n.t(context.locale, TKey.flowCancelled),
    );
    await this.showMainMenu(context);
  }

  private async submit(
    context: HandlerContext,
    state: ConversationState,
    flow: FlowDefinition,
  ): Promise<void> {
    // No CRM integration yet — record the captured request and clear the state.
    this.logger.log(
      `${LogEvent.FlowSubmitted}: ${flow.id} ${JSON.stringify({
        topic: state.topic,
        subject: state.subject,
        data: state.data,
      })}`,
      ConversationService.name,
    );
    await this.store.clear(context.user.telegramId);
    await this.responder.sendText(context, this.i18n.t(context.locale, TKey.flowSubmitted));
    await this.showMainMenu(context);
  }

  // -------------------------------------------------------------------------
  // Rendering
  // -------------------------------------------------------------------------

  private async renderStep(
    context: HandlerContext,
    state: ConversationState,
    step: FlowStep,
  ): Promise<void> {
    const t = this.i18n.scoped(context.locale);
    const prompt = this.i18n.t(context.locale, step.promptKey);
    const opts: StepControlOptions = {
      optional: step.optional,
      showBack: state.mode === 'edit' || state.history.length > 0,
    };

    switch (step.type) {
      case 'phone':
        await this.responder.sendText(context, prompt, FlowKeyboards.contact(t, opts));
        return;
      case 'location':
        await this.responder.sendText(context, prompt, FlowKeyboards.location(t, opts));
        return;
      case 'choice':
        await this.responder.sendText(context, prompt, FlowKeyboards.choice(t, step, opts));
        return;
      default:
        await this.responder.sendText(context, prompt, FlowKeyboards.text(t, opts));
    }
  }

  private async renderSummary(
    context: HandlerContext,
    state: ConversationState,
    flow: FlowDefinition,
  ): Promise<void> {
    const locale = context.locale;
    const empty = this.i18n.t(locale, TKey.flowSummaryEmpty);

    const lines: string[] = [
      this.i18n.t(locale, TKey.flowSummaryTitle),
      '',
      `<b>${this.i18n.t(locale, TKey.flowSummaryTopic)}:</b> ${this.topicLine(locale, state, flow)}`,
    ];
    for (const step of flow.steps) {
      const label = this.i18n.t(locale, step.summaryLabelKey);
      const value = state.data[step.id];
      lines.push(
        `<b>${label}:</b> ${value ? escapeHtml(this.displayValue(locale, step, value)) : empty}`,
      );
    }

    await this.responder.sendText(
      context,
      lines.join('\n'),
      FlowKeyboards.summary(this.i18n.scoped(locale)),
    );
  }

  /** Render a stored value for display (resolves choice option labels). */
  private displayValue(locale: Locale, step: FlowStep, value: string): string {
    if (step.type === 'choice') {
      const choice = (step.choices ?? []).find((c) => c.value === value);
      return choice ? this.i18n.t(locale, choice.labelKey) : value;
    }
    return value;
  }

  private topicLine(locale: Locale, state: ConversationState, flow: FlowDefinition): string {
    const topic = this.i18n.t(locale, flow.topicLabelKey(state.topic));
    const subjectKey = state.subject ? flow.subjectLabelKey?.(state.subject) : undefined;
    return subjectKey ? `${topic} — ${this.i18n.t(locale, subjectKey)}` : topic;
  }

  private async showMainMenu(context: HandlerContext): Promise<void> {
    const t = this.i18n.scoped(context.locale);
    await this.responder.sendText(
      context,
      this.i18n.t(context.locale, TKey.welcome, {
        name: escapeHtml(context.user.firstName ?? ''),
      }),
      Keyboards.mainMenu(t),
    );
  }

  // -------------------------------------------------------------------------
  // Helpers
  // -------------------------------------------------------------------------

  /** Load the active state + its flow definition, clearing orphaned state. */
  private async load(
    context: HandlerContext,
  ): Promise<{ state: ConversationState; flow: FlowDefinition } | null> {
    const state = await this.store.get(context.user.telegramId);
    if (!state) {
      return null;
    }
    const flow = this.flows.get(state.flowId);
    if (!flow) {
      await this.store.clear(context.user.telegramId);
      return null;
    }
    return { state, flow };
  }

  private currentStep(state: ConversationState, flow: FlowDefinition): FlowStep | undefined {
    if (state.mode === 'edit' && state.editStepId) {
      return this.stepById(flow, state.editStepId);
    }
    return this.stepById(flow, state.currentStepId);
  }

  private stepById(flow: FlowDefinition, id: string): FlowStep | undefined {
    return flow.steps.find((step) => step.id === id);
  }

  /** Resolve the next step from an explicit `nextStepId` or declaration order. */
  private nextStep(flow: FlowDefinition, step: FlowStep): FlowStep | undefined {
    if (step.nextStepId) {
      return this.stepById(flow, step.nextStepId);
    }
    const index = flow.steps.findIndex((candidate) => candidate.id === step.id);
    return index >= 0 ? flow.steps[index + 1] : undefined;
  }

  private usesReplyKeyboard(step: FlowStep): boolean {
    return step.type === 'phone' || step.type === 'location';
  }

  /** Reply-keyboard buttons send localized text; match it across locales. */
  private matches(text: string, key: (typeof TKey)[keyof typeof TKey]): boolean {
    return text === this.i18n.t('uz', key) || text === this.i18n.t('ru', key);
  }
}
