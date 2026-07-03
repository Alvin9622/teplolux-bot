import { Inject, Injectable, LoggerService } from '@nestjs/common';
import { MessageDirection, MessageStatus } from '@prisma/client';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { LogEvent } from '../../../logger/log-events';
import { ChatMessageRepository } from '../repositories/chat-message.repository';
import { TelegramApiService } from './telegram-api.service';
import { HandlerContext } from '../handlers/handler-context';
import { InlineKeyboardMarkup, ReplyMarkup } from '../types/telegram-api.types';

/**
 * High-level outbound messaging facade used by handlers.
 *
 * Wraps {@link TelegramApiService} and transparently persists every outbound
 * message via {@link ChatMessageRepository}, guaranteeing a complete and
 * consistent conversation history without burdening individual handlers.
 */
@Injectable()
export class TelegramResponderService {
  constructor(
    private readonly api: TelegramApiService,
    private readonly chatMessages: ChatMessageRepository,
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
  ) {}

  /** Send an HTML text message (optionally with any reply markup) and log it. */
  async sendText(context: HandlerContext, text: string, keyboard?: ReplyMarkup): Promise<void> {
    await this.maybeTyping(context, text);
    const sent = await this.api.sendMessage(context.chatId, text, {
      reply_markup: keyboard,
    });
    await this.recordOutbound(context, text, sent.message_id);
  }

  /** Send a photo with an optional HTML caption + inline keyboard, and log it. */
  async sendPhoto(
    context: HandlerContext,
    photoUrl: string,
    caption?: string,
    keyboard?: InlineKeyboardMarkup,
  ): Promise<void> {
    if (caption) {
      await this.maybeTyping(context, caption);
    }
    const sent = await this.api.sendPhoto(context.chatId, photoUrl, {
      caption,
      reply_markup: keyboard,
    });
    await this.recordOutbound(context, caption ?? `[photo ${photoUrl}]`, sent.message_id);
  }

  /** Send a message that removes any active custom reply keyboard. */
  async removeReplyKeyboard(context: HandlerContext, text: string): Promise<void> {
    const sent = await this.api.sendMessage(context.chatId, text, {
      reply_markup: { remove_keyboard: true },
    });
    await this.recordOutbound(context, text, sent.message_id);
  }

  /**
   * Edit the message the user just interacted with (inline-button press)
   * instead of sending a new one, and log the edit.
   *
   * Falls back to {@link sendText} when there is no source message to edit
   * (e.g. a callback whose original message is no longer available).
   */
  async editText(
    context: HandlerContext,
    text: string,
    keyboard?: InlineKeyboardMarkup,
  ): Promise<void> {
    const messageId = context.callbackQuery?.message?.message_id;
    if (messageId === undefined) {
      await this.sendText(context, text, keyboard);
      return;
    }

    await this.maybeTyping(context, text);
    try {
      await this.api.editMessageText(context.chatId, messageId, text, keyboard);
    } catch (error) {
      // Duplicate edit (identical content) — the message already shows the right
      // thing, so treat it as a no-op and DO NOT send a duplicate message.
      if (this.isNotModified(error)) {
        return;
      }
      // The source message is gone or can no longer be edited (deleted message,
      // expired callback, …). Recover gracefully by sending a fresh message so
      // the user still gets the response.
      this.logger.warn(
        `${LogEvent.MessageEdited} failed, falling back to a new message`,
        TelegramResponderService.name,
      );
      await this.sendText(context, text, keyboard);
      return;
    }
    await this.recordOutbound(context, text, messageId);
    this.logger.log(LogEvent.MessageEdited, TelegramResponderService.name);
  }

  /** Telegram's benign "nothing changed" response to an identical edit. */
  private isNotModified(error: unknown): boolean {
    return error instanceof Error && /not modified/i.test(error.message);
  }

  /** Send a geographic location pin and log a synthetic outbound entry. */
  async sendLocation(
    context: HandlerContext,
    latitude: number,
    longitude: number,
    keyboard?: InlineKeyboardMarkup,
  ): Promise<void> {
    const sent = await this.api.sendLocation(context.chatId, latitude, longitude, {
      reply_markup: keyboard,
    });
    await this.recordOutbound(context, `[location ${latitude},${longitude}]`, sent.message_id);
  }

  /**
   * Send a short-lived "typing…" chat action before a multi-line response.
   *
   * Guarded to multi-line text only, so single-line prompts don't overuse the
   * indicator. It is best-effort and fire-immediately (no artificial delay), so
   * it never adds more than Telegram's own sub-second action lifetime.
   */
  private async maybeTyping(context: HandlerContext, text: string): Promise<void> {
    if (text.includes('\n')) {
      await this.api.sendChatAction(context.chatId, 'typing');
    }
  }

  private async recordOutbound(
    context: HandlerContext,
    text: string,
    telegramMessageId: number,
  ): Promise<void> {
    await this.chatMessages.create({
      telegramUserId: context.user.id,
      direction: MessageDirection.OUTBOUND,
      text,
      telegramMessageId,
      status: MessageStatus.SENT,
    });
    this.logger.log(LogEvent.MessageSent, TelegramResponderService.name);
  }
}
