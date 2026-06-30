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
