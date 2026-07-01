import { TelegramUser as PersistedUser } from '@prisma/client';
import { I18nService } from '../../../i18n/i18n.service';
import { TKey } from '../../../i18n/i18n.keys';
import { CallbackData } from '../constants/callback-data.constants';
import { HandlerContext } from '../handlers/handler-context';
import { TelegramMessage } from '../types/telegram-api.types';
import { TelegramResponderService } from '../services/telegram-responder.service';
import { ConversationService } from './conversation.service';
import { ConversationStateStore } from './conversation-state.store';
import { FlowRegistry } from './flow.registry';
import { CONTACT_REQUEST_FLOW_ID, FlowAction } from './conversation.constants';
import { ConversationState, FlowDefinition } from './conversation.types';

const user: PersistedUser = {
  id: 'u1',
  telegramId: BigInt(42),
  username: null,
  firstName: 'Vasil',
  lastName: null,
  languageCode: 'uz',
  language: 'UZ',
  phone: null,
  isBlocked: false,
  createdAt: new Date(),
  updatedAt: new Date(),
  lastActivity: new Date(),
};

/** Minimal in-memory replacement for the Redis-backed state store. */
class InMemoryStore {
  private states = new Map<string, ConversationState>();
  async get(id: bigint | number): Promise<ConversationState | null> {
    return this.states.get(id.toString()) ?? null;
  }
  async set(id: bigint | number, state: ConversationState): Promise<void> {
    this.states.set(id.toString(), JSON.parse(JSON.stringify(state)));
  }
  async clear(id: bigint | number): Promise<void> {
    this.states.delete(id.toString());
  }
}

function ctx(overrides: Partial<HandlerContext> = {}): HandlerContext {
  return { chatId: 42, user, locale: 'uz', ...overrides };
}

function textMessage(text: string): TelegramMessage {
  return { message_id: 1, date: 1, chat: { id: 42, type: 'private' }, text };
}

interface Responder {
  sendText: jest.Mock;
  removeReplyKeyboard: jest.Mock;
  editText: jest.Mock;
}

function buildResponder(): Responder {
  return {
    sendText: jest.fn().mockResolvedValue(undefined),
    removeReplyKeyboard: jest.fn().mockResolvedValue(undefined),
    editText: jest.fn().mockResolvedValue(undefined),
  };
}

function buildService(store: InMemoryStore, responder: Responder, registry: FlowRegistry) {
  return new ConversationService(
    store as unknown as ConversationStateStore,
    registry,
    responder as unknown as TelegramResponderService,
    new I18nService({ warn: jest.fn() } as never),
    { log: jest.fn(), warn: jest.fn() } as never,
  );
}

describe('ConversationService — contact request flow', () => {
  let store: InMemoryStore;
  let responder: Responder;
  let service: ConversationService;

  beforeEach(() => {
    store = new InMemoryStore();
    responder = buildResponder();
    service = buildService(store, responder, new FlowRegistry());
  });

  const state = () => store.get(user.telegramId) as Promise<ConversationState>;

  it('starts a flow when a trigger callback is pressed', async () => {
    const handled = await service.handleCallback(ctx(), CallbackData.Service);

    expect(handled).toBe(true);
    expect(await service.isActive(user.telegramId)).toBe(true);
    expect(responder.sendText).toHaveBeenCalledTimes(2); // header + first prompt
  });

  it('collects every field, shows a summary, and submits', async () => {
    await service.handleCallback(ctx(), CallbackData.Service);
    await service.handleMessage(ctx({ message: textMessage('Vasil Sodiqov') }));
    await service.handleMessage(ctx({ message: textMessage('+998901234567') }));
    await service.handleMessage(ctx({ message: textMessage('Tashkent') }));

    expect((await state()).data).toMatchObject({
      fullName: 'Vasil Sodiqov',
      phone: '+998901234567',
      city: 'Tashkent',
    });

    await service.handleCallback(ctx(), FlowAction.Skip); // optional comment
    expect((await state()).mode).toBe('summary');
    expect(responder.removeReplyKeyboard).toHaveBeenCalled(); // phone step keyboard cleared

    await service.handleCallback(ctx(), FlowAction.Submit);
    expect(await service.isActive(user.telegramId)).toBe(false);
  });

  it('captures context metadata at start and carries it (product price request)', async () => {
    await service.handleCallback(ctx(), CallbackData.Boilers);

    expect((await state()).metadata).toEqual({
      requestType: 'PRICE_REQUEST',
      productCategory: 'BOILERS',
      sourceMenu: 'Products',
    });
  });

  it('captures metadata for a service request (no product)', async () => {
    await service.handleCallback(ctx(), CallbackData.Service);

    expect((await state()).metadata).toEqual({
      requestType: 'SERVICE_REQUEST',
      productCategory: undefined,
      sourceMenu: 'Service',
    });
  });

  it('shows Request Type + Selected Product, hides an empty Customer Message', async () => {
    const i18n = new I18nService({ warn: jest.fn() } as never);
    await service.handleCallback(ctx(), CallbackData.Boilers); // product request
    await service.handleMessage(ctx({ message: textMessage('Vasil Sodiqov') }));
    await service.handleMessage(ctx({ message: textMessage('+998901234567') }));
    await service.handleMessage(ctx({ message: textMessage('Tashkent') }));
    await service.handleCallback(ctx(), FlowAction.Skip); // skip customer message

    expect((await state()).mode).toBe('summary');
    const summaryText = responder.sendText.mock.calls.at(-1)?.[1] as string;
    expect(summaryText).toContain(i18n.t('uz', TKey.flowSummaryRequestType));
    expect(summaryText).toContain(i18n.t('uz', TKey.flowSummaryProduct));
    expect(summaryText).toContain(i18n.t('uz', TKey.contentProductBoilersTitle));
    // Optional Customer Message was skipped → its label must NOT appear.
    expect(summaryText).not.toContain(i18n.t('uz', TKey.flowSummaryCustomerMessage));
  });

  it('collects the optional Customer Message and shows it on the summary', async () => {
    const i18n = new I18nService({ warn: jest.fn() } as never);
    await service.handleCallback(ctx(), CallbackData.Service);
    await service.handleMessage(ctx({ message: textMessage('Vasil Sodiqov') }));
    await service.handleMessage(ctx({ message: textMessage('+998901234567') }));
    await service.handleMessage(ctx({ message: textMessage('Tashkent') }));
    // Final optional question: "What would you like to ask us?"
    await service.handleMessage(ctx({ message: textMessage('Do you deliver to Samarkand?') }));

    const current = await state();
    expect(current.mode).toBe('summary');
    expect(current.data.customerMessage).toBe('Do you deliver to Samarkand?');

    const summaryText = responder.sendText.mock.calls.at(-1)?.[1] as string;
    expect(summaryText).toContain(i18n.t('uz', TKey.flowSummaryCustomerMessage));
    expect(summaryText).toContain('Do you deliver to Samarkand?');
  });

  it('re-prompts and preserves state on invalid input', async () => {
    await service.handleCallback(ctx(), CallbackData.Service);
    responder.sendText.mockClear();

    await service.handleMessage(ctx({ message: textMessage('X') }));

    const current = await state();
    expect(current.currentStepId).toBe('fullName');
    expect(current.data.fullName).toBeUndefined();
    expect(responder.sendText).toHaveBeenCalledTimes(2); // error + re-prompt
  });

  it('accepts a shared contact for the phone step', async () => {
    await service.handleCallback(ctx(), CallbackData.Service);
    await service.handleMessage(ctx({ message: textMessage('Vasil Sodiqov') }));

    const contactMessage: TelegramMessage = {
      message_id: 2,
      date: 1,
      chat: { id: 42, type: 'private' },
      contact: { phone_number: '998901112233', first_name: 'Vasil' },
    };
    await service.handleMessage(ctx({ message: contactMessage }));

    expect((await state()).data.phone).toBe('998901112233');
    expect(responder.removeReplyKeyboard).toHaveBeenCalled();
  });

  it('supports ⬅ Back to the previous step', async () => {
    await service.handleCallback(ctx(), CallbackData.Service);
    await service.handleMessage(ctx({ message: textMessage('Vasil Sodiqov') }));
    expect((await state()).currentStepId).toBe('phone');

    await service.handleCallback(ctx(), FlowAction.Back);

    const current = await state();
    expect(current.currentStepId).toBe('fullName');
    expect(current.history).toHaveLength(0);
  });

  it('treats Back on the first step as cancel (returns to main menu)', async () => {
    await service.handleCallback(ctx(), CallbackData.Service);
    await service.handleCallback(ctx(), FlowAction.Back);

    expect(await service.isActive(user.telegramId)).toBe(false);
  });

  it('cancels at any time and clears state', async () => {
    await service.handleCallback(ctx(), CallbackData.Dealer);
    await service.handleCallback(ctx(), FlowAction.Cancel);

    expect(await service.isActive(user.telegramId)).toBe(false);
  });

  it('lets the user edit a field from the summary', async () => {
    await service.handleCallback(ctx(), CallbackData.Service);
    await service.handleMessage(ctx({ message: textMessage('Vasil Sodiqov') }));
    await service.handleMessage(ctx({ message: textMessage('+998901234567') }));
    await service.handleMessage(ctx({ message: textMessage('Tashkent') }));
    await service.handleCallback(ctx(), FlowAction.Skip);

    await service.handleCallback(ctx(), `${FlowAction.EditFieldPrefix}city`);
    expect((await state()).mode).toBe('edit');
    expect((await state()).editStepId).toBe('city');

    await service.handleMessage(ctx({ message: textMessage('Samarkand') }));
    const current = await state();
    expect(current.mode).toBe('summary');
    expect(current.data.city).toBe('Samarkand');
  });

  it('ignores flow controls when no flow is active', async () => {
    expect(await service.handleCallback(ctx(), FlowAction.Submit)).toBe(false);
    expect(await service.handleMessage(ctx({ message: textMessage('hello') }))).toBe(false);
  });
});

describe('ConversationService — engine capabilities (choice, location, next)', () => {
  let store: InMemoryStore;
  let responder: Responder;
  let service: ConversationService;

  /** A synthetic flow (registered under the existing trigger id) exercising
   *  the choice + location input types and an explicit `nextStepId`. */
  const syntheticFlow: FlowDefinition = {
    id: CONTACT_REQUEST_FLOW_ID,
    steps: [
      {
        id: 'kind',
        type: 'choice',
        promptKey: TKey.flowPromptFullName,
        summaryLabelKey: TKey.flowSummaryFullName,
        choices: [
          { value: 'buy', labelKey: TKey.menuBoilers },
          { value: 'ask', labelKey: TKey.menuRadiators },
        ],
        nextStepId: 'note', // explicitly skip the location step
        validate: (raw) => ({ ok: true, value: raw }),
      },
      {
        id: 'where',
        type: 'location',
        promptKey: TKey.flowPromptCity,
        summaryLabelKey: TKey.flowSummaryCity,
        validate: (raw) => ({ ok: true, value: raw }),
      },
      {
        id: 'note',
        type: 'text',
        optional: true,
        promptKey: TKey.flowPromptComment,
        summaryLabelKey: TKey.flowSummaryComment,
        validate: (raw) => ({ ok: true, value: raw.trim() }),
      },
    ],
    topicLabelKey: () => TKey.flowTopicService,
  };

  beforeEach(() => {
    store = new InMemoryStore();
    responder = buildResponder();
    const registry = new FlowRegistry();
    registry.register(syntheticFlow); // override the default flow for this id
    service = buildService(store, responder, registry);
  });

  const state = () => store.get(user.telegramId) as Promise<ConversationState>;

  it('accepts a valid choice and follows the configured nextStepId', async () => {
    await service.handleCallback(ctx(), CallbackData.Service);

    await service.handleCallback(ctx(), `${FlowAction.ChoicePrefix}buy`);

    const current = await state();
    expect(current.data.kind).toBe('buy');
    // nextStepId jumped straight to 'note', skipping the 'where' location step.
    expect(current.currentStepId).toBe('note');
  });

  it('rejects an invalid choice value and stays on the step', async () => {
    await service.handleCallback(ctx(), CallbackData.Service);

    await service.handleCallback(ctx(), `${FlowAction.ChoicePrefix}bogus`);

    expect((await state()).currentStepId).toBe('kind');
    expect((await state()).data.kind).toBeUndefined();
  });

  it('captures a shared location on a location step', async () => {
    // Drive to the 'where' step via Back from 'note' after choosing.
    await service.handleCallback(ctx(), CallbackData.Service);
    await service.handleCallback(ctx(), `${FlowAction.ChoicePrefix}ask`); // -> note (nextStepId)
    await service.handleCallback(ctx(), FlowAction.Back); // back -> kind
    // Re-select but this time we want to reach 'where'; drive it directly.
    const current = await state();
    current.currentStepId = 'where';
    current.history = ['kind'];
    await store.set(user.telegramId, current);

    const locationMessage: TelegramMessage = {
      message_id: 3,
      date: 1,
      chat: { id: 42, type: 'private' },
      location: { latitude: 41.31, longitude: 69.24 },
    };
    await service.handleMessage(ctx({ message: locationMessage }));

    expect((await state()).data.where).toBe('41.31,69.24');
    expect(responder.removeReplyKeyboard).toHaveBeenCalled();
  });
});
