import { Test, TestingModule } from '@nestjs/testing';
import { TelegramUser as PersistedUser } from '@prisma/client';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { BotCommand } from '../constants/commands.constants';
import { CallbackData } from '../constants/callback-data.constants';
import { I18nService } from '../../../i18n/i18n.service';
import { COMMAND_HANDLERS, CommandHandler } from '../handlers/command-handler.interface';
import { ChatMessageRepository } from '../repositories/chat-message.repository';
import { ConversationService } from '../conversation/conversation.service';
import { ContentService } from '../content/content.service';
import { FaqPresenterService } from '../faq/faq-presenter.service';
import { AnalyticsService } from '../analytics/analytics.service';
import { TelegramApiService } from './telegram-api.service';
import { TelegramCallbackService } from './telegram-callback.service';
import { TelegramResponderService } from './telegram-responder.service';
import { TelegramUpdateService } from './telegram-update.service';
import { TelegramUserService } from './telegram-user.service';
import { TelegramUpdateDto } from '../dto/telegram-update.dto';

const persistedUser: PersistedUser = {
  id: 'user-uuid',
  telegramId: BigInt(42),
  username: 'tester',
  firstName: 'Test',
  lastName: null,
  languageCode: 'en',
  language: null,
  phone: null,
  isBlocked: false,
  createdAt: new Date(),
  updatedAt: new Date(),
  lastActivity: new Date(),
};

function messageUpdate(text: string): TelegramUpdateDto {
  return {
    update_id: 1,
    message: {
      message_id: 100,
      date: 1700000000,
      chat: { id: 42, type: 'private' },
      from: { id: 42, is_bot: false, first_name: 'Test', username: 'tester' },
      text,
    },
  };
}

describe('TelegramUpdateService', () => {
  let service: TelegramUpdateService;
  let startHandler: CommandHandler;
  let chatMessages: { create: jest.Mock };
  let responder: { sendText: jest.Mock };
  let callbacks: { handle: jest.Mock };
  let conversation: {
    isActive: jest.Mock;
    abort: jest.Mock;
    handleMessage: jest.Mock;
    handleCallback: jest.Mock;
  };
  let content: { handleCallback: jest.Mock };
  let faqPresenter: { handleCallback: jest.Mock };
  let api: { answerCallbackQuery: jest.Mock };

  beforeEach(async () => {
    startHandler = { command: BotCommand.Start, handle: jest.fn().mockResolvedValue(undefined) };
    chatMessages = { create: jest.fn().mockResolvedValue(undefined) };
    responder = { sendText: jest.fn().mockResolvedValue(undefined) };
    callbacks = { handle: jest.fn().mockResolvedValue(true) };
    conversation = {
      isActive: jest.fn().mockResolvedValue(false),
      abort: jest.fn().mockResolvedValue(undefined),
      handleMessage: jest.fn().mockResolvedValue(false),
      handleCallback: jest.fn().mockResolvedValue(false),
    };
    content = { handleCallback: jest.fn().mockResolvedValue(false) };
    faqPresenter = { handleCallback: jest.fn().mockResolvedValue(false) };
    api = { answerCallbackQuery: jest.fn().mockResolvedValue(undefined) };

    const moduleRef: TestingModule = await Test.createTestingModule({
      providers: [
        TelegramUpdateService,
        { provide: COMMAND_HANDLERS, useValue: [startHandler] },
        {
          provide: TelegramUserService,
          useValue: { upsertFromTelegram: jest.fn().mockResolvedValue(persistedUser) },
        },
        { provide: ChatMessageRepository, useValue: chatMessages },
        { provide: TelegramResponderService, useValue: responder },
        { provide: TelegramCallbackService, useValue: callbacks },
        { provide: ConversationService, useValue: conversation },
        { provide: ContentService, useValue: content },
        { provide: FaqPresenterService, useValue: faqPresenter },
        {
          provide: AnalyticsService,
          useValue: { track: jest.fn(), trackMenu: jest.fn(), trackFlow: jest.fn() },
        },
        { provide: TelegramApiService, useValue: api },
        {
          provide: I18nService,
          useValue: {
            t: jest.fn().mockReturnValue('translated'),
            scoped: jest.fn().mockReturnValue(() => 'label'),
          },
        },
        {
          provide: WINSTON_MODULE_NEST_PROVIDER,
          useValue: { log: jest.fn(), warn: jest.fn(), error: jest.fn(), debug: jest.fn() },
        },
      ],
    }).compile();

    service = moduleRef.get(TelegramUpdateService);
  });

  it('routes a /start message to the start handler and records the inbound message', async () => {
    await service.process(messageUpdate('/start'));

    expect(chatMessages.create).toHaveBeenCalledWith(
      expect.objectContaining({ command: 'start', direction: 'INBOUND' }),
    );
    expect(startHandler.handle).toHaveBeenCalledTimes(1);
  });

  it('strips a bot mention from the command (/start@bot)', async () => {
    await service.process(messageUpdate('/start@teplolux_bot'));
    expect(startHandler.handle).toHaveBeenCalledTimes(1);
  });

  it('falls back to the menu for an unknown command', async () => {
    await service.process(messageUpdate('/doesnotexist'));
    expect(startHandler.handle).not.toHaveBeenCalled();
    expect(responder.sendText).toHaveBeenCalled();
  });

  it('sends a fallback message for free-form text', async () => {
    await service.process(messageUpdate('hello there'));
    expect(responder.sendText).toHaveBeenCalled();
    expect(startHandler.handle).not.toHaveBeenCalled();
  });

  it('acknowledges and routes a callback query', async () => {
    await service.process({
      update_id: 2,
      callback_query: {
        id: 'cbq-1',
        from: { id: 42, is_bot: false, first_name: 'Test' },
        data: CallbackData.Boilers,
        message: { message_id: 7, date: 1, chat: { id: 42, type: 'private' } },
      },
    });

    expect(api.answerCallbackQuery).toHaveBeenCalledWith('cbq-1', expect.any(Object));
    expect(callbacks.handle).toHaveBeenCalledWith(expect.any(Object), CallbackData.Boilers);
  });

  it('ignores non-private chats', async () => {
    await service.process({
      update_id: 3,
      message: {
        message_id: 1,
        date: 1,
        chat: { id: -100, type: 'group' },
        from: { id: 42, is_bot: false, first_name: 'Test' },
        text: '/start',
      },
    });
    expect(startHandler.handle).not.toHaveBeenCalled();
  });
});
