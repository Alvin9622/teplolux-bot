import { Inject, Injectable, LoggerService } from '@nestjs/common';
import { MessageDirection, MessageStatus, TelegramUser as PersistedUser } from '@prisma/client';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { LogEvent } from '../../../logger/log-events';
import { BotCommandName } from '../constants/commands.constants';
import { BotMessage } from '../constants/messages.constants';
import { Keyboards } from '../keyboards/main-menu.keyboard';
import { TelegramUpdateDto } from '../dto/telegram-update.dto';
import { COMMAND_HANDLERS, CommandHandler } from '../handlers/command-handler.interface';
import { HandlerContext } from '../handlers/handler-context';
import { ChatMessageRepository } from '../repositories/chat-message.repository';
import { TelegramCallbackQuery, TelegramMessage, TelegramUser } from '../types/telegram-api.types';
import { TelegramApiService } from './telegram-api.service';
import { TelegramCallbackService } from './telegram-callback.service';
import { TelegramResponderService } from './telegram-responder.service';
import { TelegramUserService } from './telegram-user.service';

/**
 * Central dispatcher that turns a validated Telegram update into side effects.
 *
 * Responsibilities:
 *  - persist the user and the inbound message,
 *  - route messages to the correct {@link CommandHandler} (built into a map for
 *    O(1) lookup and Open/Closed extensibility),
 *  - route inline-button presses through {@link TelegramCallbackService},
 *  - fall back gracefully for unknown input.
 *
 * Update processing is deliberately decoupled from the HTTP request: the
 * controller acknowledges Telegram immediately and processing runs afterwards.
 */
@Injectable()
export class TelegramUpdateService {
  private readonly commandMap: ReadonlyMap<BotCommandName, CommandHandler>;

  constructor(
    @Inject(COMMAND_HANDLERS) handlers: CommandHandler[],
    private readonly users: TelegramUserService,
    private readonly chatMessages: ChatMessageRepository,
    private readonly responder: TelegramResponderService,
    private readonly callbacks: TelegramCallbackService,
    private readonly api: TelegramApiService,
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
  ) {
    this.commandMap = new Map(handlers.map((handler) => [handler.command, handler]));
  }

  /** Entry point: process a single, already-validated update. */
  async process(update: TelegramUpdateDto): Promise<void> {
    this.logger.log(
      `${LogEvent.IncomingUpdate}: update_id=${update.update_id} type=${this.updateType(update)}`,
      TelegramUpdateService.name,
    );

    if (update.callback_query) {
      await this.handleCallbackQuery(update.callback_query as TelegramCallbackQuery);
      return;
    }

    const message = (update.message ?? update.edited_message) as TelegramMessage | undefined;
    if (message) {
      await this.handleMessage(message);
      return;
    }

    this.logger.debug?.('Update contained no actionable payload', TelegramUpdateService.name);
  }

  // -------------------------------------------------------------------------
  // Message handling
  // -------------------------------------------------------------------------

  private async handleMessage(message: TelegramMessage): Promise<void> {
    if (!message.from || message.chat.type !== 'private') {
      // Only private 1:1 conversations are serviced by the assistant for now.
      return;
    }

    const user = await this.users.upsertFromTelegram(message.from);
    const command = this.extractCommand(message);

    await this.chatMessages.create({
      telegramUserId: user.id,
      direction: MessageDirection.INBOUND,
      text: message.text ?? null,
      telegramMessageId: message.message_id,
      command,
      status: MessageStatus.RECEIVED,
    });
    this.logger.log(LogEvent.MessageReceived, TelegramUpdateService.name);

    const context = this.buildContext(user, message.chat.id, message, undefined, message.text);

    if (command) {
      await this.dispatchCommand(command, context);
      return;
    }

    // Free-form text with no command — friendly fallback for now.
    await this.responder.sendText(context, BotMessage.fallback, Keyboards.mainMenu());
  }

  private async dispatchCommand(command: string, context: HandlerContext): Promise<void> {
    const handler = this.commandMap.get(command as BotCommandName);
    if (!handler) {
      this.logger.warn(`${LogEvent.UnknownCommand}: /${command}`, TelegramUpdateService.name);
      await this.responder.sendText(context, BotMessage.unknownCommand, Keyboards.mainMenu());
      return;
    }
    await handler.handle(context);
    this.logger.log(`${LogEvent.CommandHandled}: /${command}`, TelegramUpdateService.name);
  }

  // -------------------------------------------------------------------------
  // Callback (inline button) handling
  // -------------------------------------------------------------------------

  private async handleCallbackQuery(callback: TelegramCallbackQuery): Promise<void> {
    this.logger.log(
      `${LogEvent.CallbackQueryReceived}: data="${callback.data ?? ''}" from=${callback.from.id}`,
      TelegramUpdateService.name,
    );

    const user = await this.users.upsertFromTelegram(callback.from);
    const chatId = callback.message?.chat.id ?? callback.from.id;
    const context = this.buildContext(user, chatId, undefined, callback, callback.data);

    // Always acknowledge so the Telegram client stops its loading spinner.
    await this.api.answerCallbackQuery(callback.id, { text: BotMessage.callbackAcknowledged });

    if (!callback.data) {
      return;
    }

    const handled = await this.callbacks.handle(context, callback.data);
    if (!handled) {
      this.logger.warn(
        `${LogEvent.UnknownCommand}: callback "${callback.data}"`,
        TelegramUpdateService.name,
      );
      await this.responder.sendText(context, BotMessage.fallback, Keyboards.mainMenu());
    }
  }

  // -------------------------------------------------------------------------
  // Helpers
  // -------------------------------------------------------------------------

  /** Human-readable update kind for logging. */
  private updateType(update: TelegramUpdateDto): string {
    if (update.callback_query) {
      return 'callback_query';
    }
    if (update.message) {
      return 'message';
    }
    if (update.edited_message) {
      return 'edited_message';
    }
    return 'unknown';
  }

  /** Extract a bare command keyword (e.g. `start`) from a `/command@bot args` message. */
  private extractCommand(message: TelegramMessage): string | null {
    const text = message.text?.trim();
    if (!text || !text.startsWith('/')) {
      return null;
    }
    const token = text.split(/\s+/)[0]; // "/start@bot"
    const command = token.slice(1).split('@')[0].toLowerCase();
    return command.length > 0 ? command : null;
  }

  private buildContext(
    user: PersistedUser,
    chatId: number,
    message?: TelegramMessage,
    callbackQuery?: TelegramCallbackQuery,
    text?: string,
  ): HandlerContext {
    return { user, chatId, message, callbackQuery, text };
  }
}

/** Re-exported for typing convenience in tests. */
export type { TelegramUser };
