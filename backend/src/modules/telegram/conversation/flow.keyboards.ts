import { TKey } from '../../../i18n/i18n.keys';
import { Translator } from '../../../i18n/i18n.types';
import {
  InlineKeyboardButton,
  InlineKeyboardMarkup,
  KeyboardButton,
  ReplyKeyboardMarkup,
} from '../types/telegram-api.types';
import { FlowAction } from './conversation.constants';
import { FlowDefinition, FlowStep } from './conversation.types';

/** Options controlling which navigation controls a step shows. */
export interface StepControlOptions {
  readonly optional?: boolean;
  readonly showBack: boolean;
}

/** Inline "⬅ Back" (optional) + "❌ Cancel" navigation row. */
function inlineNavRow(t: Translator, showBack: boolean): InlineKeyboardButton[] {
  const row: InlineKeyboardButton[] = [];
  if (showBack) {
    row.push({ text: t(TKey.flowButtonBack), callback_data: FlowAction.Back });
  }
  row.push({ text: t(TKey.flowButtonCancel), callback_data: FlowAction.Cancel });
  return row;
}

/** Reply-keyboard "⬅ Back" (optional) + "❌ Cancel" navigation row. */
function replyNavRow(t: Translator, showBack: boolean): KeyboardButton[] {
  const row: KeyboardButton[] = [];
  if (showBack) {
    row.push({ text: t(TKey.flowButtonBack) });
  }
  row.push({ text: t(TKey.flowButtonCancel) });
  return row;
}

/**
 * Keyboard factories for the generic conversation flow. Labels are localised
 * via the supplied {@link Translator}; all controls reuse the `flow:` callbacks.
 */
export const FlowKeyboards = {
  /** Controls for a plain text step: optional Skip, then Back/Cancel. */
  text(t: Translator, opts: StepControlOptions): InlineKeyboardMarkup {
    const rows: InlineKeyboardButton[][] = [];
    if (opts.optional) {
      rows.push([{ text: t(TKey.flowButtonSkip), callback_data: FlowAction.Skip }]);
    }
    rows.push(inlineNavRow(t, opts.showBack));
    return { inline_keyboard: rows };
  },

  /** A button per choice option, then Back/Cancel. */
  choice(t: Translator, step: FlowStep, opts: StepControlOptions): InlineKeyboardMarkup {
    const rows: InlineKeyboardButton[][] = (step.choices ?? []).map((choice) => [
      { text: t(choice.labelKey), callback_data: `${FlowAction.ChoicePrefix}${choice.value}` },
    ]);
    if (opts.optional) {
      rows.push([{ text: t(TKey.flowButtonSkip), callback_data: FlowAction.Skip }]);
    }
    rows.push(inlineNavRow(t, opts.showBack));
    return { inline_keyboard: rows };
  },

  /** Reply keyboard offering the native Telegram contact-share button. */
  contact(t: Translator, opts: StepControlOptions): ReplyKeyboardMarkup {
    return {
      keyboard: [
        [{ text: t(TKey.flowButtonShareContact), request_contact: true }],
        replyNavRow(t, opts.showBack),
      ],
      resize_keyboard: true,
      one_time_keyboard: true,
    };
  },

  /** Reply keyboard offering the native Telegram location-share button. */
  location(t: Translator, opts: StepControlOptions): ReplyKeyboardMarkup {
    return {
      keyboard: [
        [{ text: t(TKey.flowButtonShareLocation), request_location: true }],
        replyNavRow(t, opts.showBack),
      ],
      resize_keyboard: true,
      one_time_keyboard: true,
    };
  },

  /** Confirmation controls shown under the summary. */
  summary(t: Translator): InlineKeyboardMarkup {
    return {
      inline_keyboard: [
        [
          { text: t(TKey.flowButtonSubmit), callback_data: FlowAction.Submit },
          { text: t(TKey.flowButtonEdit), callback_data: FlowAction.Edit },
        ],
        [{ text: t(TKey.flowButtonCancel), callback_data: FlowAction.Cancel }],
      ],
    };
  },

  /** One button per editable field plus Cancel. */
  editChoose(t: Translator, flow: FlowDefinition): InlineKeyboardMarkup {
    const rows = flow.steps.map((step) => [
      { text: t(step.summaryLabelKey), callback_data: `${FlowAction.EditFieldPrefix}${step.id}` },
    ]);
    rows.push([{ text: t(TKey.flowButtonCancel), callback_data: FlowAction.Cancel }]);
    return { inline_keyboard: rows };
  },
} as const;
