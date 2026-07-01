import { Inject, Injectable, LoggerService } from '@nestjs/common';
import { MessageDirection, MessageStatus, TelegramUser as PersistedUser } from '@prisma/client';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { LogEvent } from '../../../logger/log-events';
import { I18nService } from '../../../i18n/i18n.service';
import { TKey } from '../../../i18n/i18n.keys';
import { DEFAULT_LOCALE, Locale, prismaLanguageToLocale } from '../../../i18n/i18n.types';
import { BotCommandName } from '../constants/commands.constants';
import { Keyboards } from '../keyboards/main-menu.keyboard';
import { TelegramUpdateDto } from '../dto/telegram-update.dto';
import { COMMAND_HANDLERS, CommandHandler } from '../handlers/command-handler.interface';
import { HandlerContext } from '../handlers/handler-context';
import { ChatMessageRepository } from '../repositories/chat-message.repository';
import { TelegramCallbackQuery, TelegramMessage, TelegramUser } from '../types/telegram-api.types';
import { ConversationService } from '../conversation/conversation.service';
import { ContentService } from '../content/content.service';
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
    private readonly conversation: ConversationService,
    private readonly content: ContentService,
    private readonly api: TelegramApiService,
    private readonly i18n: I18nService,
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
      // A command interrupts any in-progress guided conversation.
      if (await this.conversation.isActive(user.telegramId)) {
        await this.conversation.abort(user.telegramId);
      }
      await this.dispatchCommand(command, context);
      return;
    }

    // An active conversation consumes step answers (text or shared contact).
    if (await this.conversation.handleMessage(context)) {
      return;
    }

    // Free-form text with no command and no active flow — friendly fallback.
    await this.responder.sendText(
      context,
      this.i18n.t(context.locale, TKey.fallback),
      Keyboards.mainMenu(this.i18n.scoped(context.locale)),
    );
  }

  private async dispatchCommand(command: string, context: HandlerContext): Promise<void> {
    const handler = this.commandMap.get(command as BotCommandName);
    if (!handler) {
      this.logger.warn(`${LogEvent.UnknownCommand}: /${command}`, TelegramUpdateService.name);
      await this.responder.sendText(
        context,
        this.i18n.t(context.locale, TKey.unknownCommand),
        Keyboards.mainMenu(this.i18n.scoped(context.locale)),
      );
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
    await this.api.answerCallbackQuery(callback.id, {
      text: this.i18n.t(context.locale, TKey.callbackAcknowledged),
    });

    if (!callback.data) {
      return;
    }

    // The conversation engine gets first refusal: it owns flow triggers
    // (product/service/dealer/operator) and the flow control buttons.
    if (await this.conversation.handleCallback(context, callback.data)) {
      return;
    }

    // The content module owns informational page navigation (`content:*`).
    if (await this.content.handleCallback(context, callback.data)) {
      return;
    }

    const handled = await this.callbacks.handle(context, callback.data);
    if (!handled) {
      this.logger.warn(
        `${LogEvent.UnknownCommand}: callback "${callback.data}"`,
        TelegramUpdateService.name,
      );
      await this.responder.sendText(
        context,
        this.i18n.t(context.locale, TKey.fallback),
        Keyboards.mainMenu(this.i18n.scoped(context.locale)),
      );
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
    return { user, chatId, message, callbackQuery, text, locale: this.resolveLocale(user) };
  }

  /**
   * Resolve the locale for an interaction: the user's explicit choice when set,
   * otherwise a best-effort guess from Telegram's reported language code,
   * finally the default locale.
   */
  private resolveLocale(user: PersistedUser): Locale {
    const selected = prismaLanguageToLocale(user.language);
    if (selected) {
      return selected;
    }
    return user.languageCode?.toLowerCase().startsWith('ru') ? 'ru' : DEFAULT_LOCALE;
  }
}

/** Re-exported for typing convenience in tests. */
export type { TelegramUser };
