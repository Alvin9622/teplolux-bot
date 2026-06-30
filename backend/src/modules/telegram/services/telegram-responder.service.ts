import { Inject, Injectable, LoggerService } from '@nestjs/common';
import { MessageDirection, MessageStatus } from '@prisma/client';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { LogEvent } from '../../../logger/log-events';
import { ChatMessageRepository } from '../repositories/chat-message.repository';
import { TelegramApiService } from './telegram-api.service';
import { HandlerContext } from '../handlers/handler-context';
import { InlineKeyboardMarkup } from '../types/telegram-api.types';

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

  /** Send an HTML text message (optionally with an inline keyboard) and log it. */
  async sendText(
    context: HandlerContext,
    text: string,
    keyboard?: InlineKeyboardMarkup,
  ): Promise<void> {
    const sent = await this.api.sendMessage(context.chatId, text, {
      reply_markup: keyboard,
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

    await this.api.editMessageText(context.chatId, messageId, text, keyboard);
    await this.recordOutbound(context, text, messageId);
    this.logger.log(LogEvent.MessageEdited, TelegramResponderService.name);
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
