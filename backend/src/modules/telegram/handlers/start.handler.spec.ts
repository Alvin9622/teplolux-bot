import { TelegramUser as PersistedUser } from '@prisma/client';
import { TelegramResponderService } from '../services/telegram-responder.service';
import { HandlerContext } from './handler-context';
import { StartCommandHandler } from './start.handler';

describe('StartCommandHandler', () => {
  const user: PersistedUser = {
    id: 'u1',
    telegramId: BigInt(1),
    username: null,
    firstName: 'Vasil',
    lastName: null,
    languageCode: 'uz',
    phone: null,
    isBlocked: false,
    createdAt: new Date(),
    updatedAt: new Date(),
    lastActivity: new Date(),
  };

  const context: HandlerContext = { chatId: 1, user };

  it('greets the user with the main menu', async () => {
    const responder = { sendText: jest.fn().mockResolvedValue(undefined) };
    const logger = { log: jest.fn() };
    const handler = new StartCommandHandler(
      responder as unknown as TelegramResponderService,
      logger as never,
    );

    await handler.handle(context);

    expect(responder.sendText).toHaveBeenCalledTimes(1);
    const [, text, keyboard] = responder.sendText.mock.calls[0];
    expect(text).toContain('Vasil');
    expect(keyboard.inline_keyboard.length).toBeGreaterThan(0);
  });
});
