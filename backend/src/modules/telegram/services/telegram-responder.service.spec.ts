import { TelegramUser as PersistedUser } from '@prisma/client';
import { ChatMessageRepository } from '../repositories/chat-message.repository';
import { HandlerContext } from '../handlers/handler-context';
import { TelegramApiService } from './telegram-api.service';
import { TelegramResponderService } from './telegram-responder.service';

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

describe('TelegramResponderService.editText', () => {
  let api: { editMessageText: jest.Mock; sendMessage: jest.Mock; sendChatAction: jest.Mock };
  let chatMessages: { create: jest.Mock };
  let responder: TelegramResponderService;

  beforeEach(() => {
    api = {
      editMessageText: jest.fn().mockResolvedValue(undefined),
      sendMessage: jest.fn().mockResolvedValue({ message_id: 123 }),
      sendChatAction: jest.fn().mockResolvedValue(undefined),
    };
    chatMessages = { create: jest.fn().mockResolvedValue(undefined) };
    responder = new TelegramResponderService(
      api as unknown as TelegramApiService,
      chatMessages as unknown as ChatMessageRepository,
      { log: jest.fn(), warn: jest.fn() } as never,
    );
  });

  const callbackContext: HandlerContext = {
    chatId: 7,
    user,
    locale: 'uz',
    callbackQuery: {
      id: 'cbq',
      from: { id: 7, is_bot: false, first_name: 'Vasil' },
      message: { message_id: 99, date: 1, chat: { id: 7, type: 'private' } },
    },
  };

  it('edits the source message when a callback message is present', async () => {
    const context: HandlerContext = {
      chatId: 7,
      user,
      locale: 'uz',
      callbackQuery: {
        id: 'cbq',
        from: { id: 7, is_bot: false, first_name: 'Vasil' },
        message: { message_id: 99, date: 1, chat: { id: 7, type: 'private' } },
      },
    };

    await responder.editText(context, 'updated');

    expect(api.editMessageText).toHaveBeenCalledWith(7, 99, 'updated', undefined);
    expect(api.sendMessage).not.toHaveBeenCalled();
    expect(chatMessages.create).toHaveBeenCalled();
  });

  it('falls back to sending a new message when there is nothing to edit', async () => {
    const context: HandlerContext = { chatId: 7, user, locale: 'uz' };

    await responder.editText(context, 'hello');

    expect(api.sendMessage).toHaveBeenCalled();
    expect(api.editMessageText).not.toHaveBeenCalled();
  });

  it('recovers gracefully when the source message can no longer be edited', async () => {
    // e.g. the user deleted the message or the callback expired.
    api.editMessageText.mockRejectedValueOnce(
      new Error(
        'Telegram API "editMessageText" request failed: Bad Request: message to edit not found',
      ),
    );

    await responder.editText(callbackContext, 'updated');

    // Falls back to a fresh message so the user still gets the response.
    expect(api.sendMessage).toHaveBeenCalledTimes(1);
  });

  it('treats an identical edit ("not modified") as a no-op — no duplicate message', async () => {
    api.editMessageText.mockRejectedValueOnce(
      new Error(
        'Telegram API "editMessageText" request failed: Bad Request: message is not modified',
      ),
    );

    await responder.editText(callbackContext, 'same');

    // No duplicate: neither a fallback send nor an outbound record.
    expect(api.sendMessage).not.toHaveBeenCalled();
  });

  it('sends a typing action before a multi-line response', async () => {
    const context: HandlerContext = { chatId: 7, user, locale: 'uz' };

    await responder.sendText(context, 'line one\nline two');

    expect(api.sendChatAction).toHaveBeenCalledWith(7, 'typing');
  });

  it('does not send a typing action for a single-line response', async () => {
    const context: HandlerContext = { chatId: 7, user, locale: 'uz' };

    await responder.sendText(context, 'just one line');

    expect(api.sendChatAction).not.toHaveBeenCalled();
  });
});
