import { TelegramUser as PersistedUser } from '@prisma/client';
import { I18nService } from '../../../i18n/i18n.service';
import { CallbackData } from '../constants/callback-data.constants';
import { HandlerContext } from '../handlers/handler-context';
import { TelegramCallbackService } from './telegram-callback.service';
import { TelegramResponderService } from './telegram-responder.service';
import { TelegramUserService } from './telegram-user.service';

const user: PersistedUser = {
  id: 'u1',
  telegramId: BigInt(7),
  username: null,
  firstName: 'Vasil',
  lastName: null,
  languageCode: 'uz',
  language: null,
  phone: null,
  isBlocked: false,
  createdAt: new Date(),
  updatedAt: new Date(),
  lastActivity: new Date(),
};

/** A callback context whose source message can be edited in place. */
function callbackContext(): HandlerContext {
  return {
    chatId: 7,
    user,
    locale: 'uz',
    callbackQuery: {
      id: 'cbq',
      from: { id: 7, is_bot: false, first_name: 'Vasil' },
      message: { message_id: 99, date: 1, chat: { id: 7, type: 'private' } },
    },
  };
}

describe('TelegramCallbackService', () => {
  let responder: { editText: jest.Mock; sendText: jest.Mock; sendLocation: jest.Mock };
  let users: { setLanguage: jest.Mock };
  let service: TelegramCallbackService;

  beforeEach(() => {
    responder = {
      editText: jest.fn().mockResolvedValue(undefined),
      sendText: jest.fn().mockResolvedValue(undefined),
      sendLocation: jest.fn().mockResolvedValue(undefined),
    };
    users = { setLanguage: jest.fn().mockResolvedValue(user) };
    const i18n = {
      t: jest.fn((_locale: string, key: string) => key),
      scoped: jest.fn(() => (key: string) => key),
    };
    service = new TelegramCallbackService(
      responder as unknown as TelegramResponderService,
      users as unknown as TelegramUserService,
      i18n as unknown as I18nService,
    );
  });

  it('edits the current message (never sends a new one) on a category press', async () => {
    const handled = await service.handle(callbackContext(), CallbackData.Boilers);

    expect(handled).toBe(true);
    expect(responder.editText).toHaveBeenCalledTimes(1);
    expect(responder.sendText).not.toHaveBeenCalled();
  });

  it('opens the language selection screen on "Change language"', async () => {
    await service.handle(callbackContext(), CallbackData.ChangeLanguage);

    expect(responder.editText).toHaveBeenCalledTimes(1);
    const [, , keyboard] = responder.editText.mock.calls[0];
    // Two language options (Uzbek + Russian).
    expect(keyboard.inline_keyboard).toHaveLength(2);
  });

  it('persists the chosen language and shows the main menu', async () => {
    await service.handle(callbackContext(), CallbackData.SelectLangRu);

    expect(users.setLanguage).toHaveBeenCalledWith('u1', 'ru');
    expect(responder.editText).toHaveBeenCalledTimes(1);
    const [, , keyboard] = responder.editText.mock.calls[0];
    expect(keyboard.inline_keyboard.length).toBeGreaterThan(1);
  });

  it('restores the main menu on "Back to menu"', async () => {
    await service.handle(callbackContext(), CallbackData.BackToMenu);

    expect(responder.editText).toHaveBeenCalledTimes(1);
    const [, , keyboard] = responder.editText.mock.calls[0];
    expect(keyboard.inline_keyboard.length).toBeGreaterThan(1);
  });

  it('edits in place for the Location button (no new message / pin)', async () => {
    await service.handle(callbackContext(), CallbackData.Location);

    expect(responder.editText).toHaveBeenCalledTimes(1);
    expect(responder.sendLocation).not.toHaveBeenCalled();
  });

  it('handles every defined callback value', async () => {
    for (const data of Object.values(CallbackData)) {
      responder.editText.mockClear();
      const handled = await service.handle(callbackContext(), data);
      expect(handled).toBe(true);
      expect(responder.editText).toHaveBeenCalledTimes(1);
    }
  });

  it('reports unknown callbacks as unhandled', async () => {
    const handled = await service.handle(callbackContext(), 'totally:unknown');
    expect(handled).toBe(false);
  });
});
