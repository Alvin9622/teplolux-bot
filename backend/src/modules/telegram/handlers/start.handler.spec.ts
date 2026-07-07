import { Language, TelegramUser as PersistedUser } from '@prisma/client';
import { I18nService } from '../../../i18n/i18n.service';
import { TelegramResponderService } from '../services/telegram-responder.service';
import { HandlerContext } from './handler-context';
import { StartCommandHandler } from './start.handler';

function buildUser(language: Language | null): PersistedUser {
  return {
    id: 'u1',
    telegramId: BigInt(1),
    username: null,
    firstName: 'Vasil',
    lastName: null,
    languageCode: 'uz',
    language,
    phone: null,
    isBlocked: false,
    createdAt: new Date(),
    updatedAt: new Date(),
    lastActivity: new Date(),
  };
}

describe('StartCommandHandler', () => {
  let responder: { sendText: jest.Mock };
  let i18n: I18nService;
  let handler: StartCommandHandler;

  beforeEach(() => {
    responder = { sendText: jest.fn().mockResolvedValue(undefined) };
    i18n = new I18nService({ warn: jest.fn() } as never);
    handler = new StartCommandHandler(responder as unknown as TelegramResponderService, i18n, {
      log: jest.fn(),
    } as never);
  });

  it('shows the language selection screen on first contact', async () => {
    const context: HandlerContext = { chatId: 1, user: buildUser(null), locale: 'uz' };

    await handler.handle(context);

    expect(responder.sendText).toHaveBeenCalledTimes(1);
    const [, , keyboard] = responder.sendText.mock.calls[0];
    // Two native-language options.
    expect(keyboard.inline_keyboard).toHaveLength(2);
    expect(JSON.stringify(keyboard)).toContain('lang:uz');
    expect(JSON.stringify(keyboard)).toContain('lang:ru');
  });

  it('shows the customer-type selection once a language is set', async () => {
    const context: HandlerContext = { chatId: 1, user: buildUser(Language.UZ), locale: 'uz' };

    await handler.handle(context);

    expect(responder.sendText).toHaveBeenCalledTimes(1);
    const [, text, keyboard] = responder.sendText.mock.calls[0];
    expect(text).toContain('Assalomu');
    expect(keyboard.inline_keyboard.length).toBeGreaterThan(1);
    // The six customer types are offered as flow triggers.
    expect(JSON.stringify(keyboard)).toContain('ctype:individual');
    expect(JSON.stringify(keyboard)).toContain('ctype:company');
  });

  it('renders the Russian welcome when the user chose Russian', async () => {
    const context: HandlerContext = { chatId: 1, user: buildUser(Language.RU), locale: 'ru' };

    await handler.handle(context);

    const [, text] = responder.sendText.mock.calls[0];
    expect(text).toContain('Добро пожаловать');
  });
});
