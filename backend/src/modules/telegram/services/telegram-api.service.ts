import { Inject, Injectable, LoggerService, OnModuleInit } from '@nestjs/common';
import axios, { AxiosInstance, isAxiosError } from 'axios';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { AppConfigService } from '../../../config/app-config.service';
import { LogEvent } from '../../../logger/log-events';
import { TelegramApiException } from '../../../common/exceptions';
import {
  AnswerCallbackQueryOptions,
  BotCommandDefinition,
  InlineKeyboardMarkup,
  SendLocationOptions,
  SendMessageOptions,
  TelegramApiResponse,
  TelegramMessage,
  TelegramWebhookInfo,
} from '../types/telegram-api.types';
import { BOT_COMMAND_DESCRIPTIONS } from '../constants/commands.constants';

const TELEGRAM_API_BASE = 'https://api.telegram.org';
const DEFAULT_TIMEOUT_MS = 10_000;

/**
 * Typed client for the Telegram Bot API.
 *
 * Wraps Axios with the bot token, centralised error handling and logging. Every
 * outbound interaction with Telegram goes through this service so retries,
 * tracing and rate-limit handling can evolve in one place.
 */
@Injectable()
export class TelegramApiService implements OnModuleInit {
  private readonly http: AxiosInstance;

  constructor(
    private readonly configService: AppConfigService,
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
  ) {
    const { botToken } = this.configService.telegram;
    this.http = axios.create({
      baseURL: `${TELEGRAM_API_BASE}/bot${botToken}`,
      timeout: DEFAULT_TIMEOUT_MS,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  /**
   * On startup, optionally register the webhook with Telegram and publish the
   * command list. Controlled by `TELEGRAM_SET_WEBHOOK_ON_STARTUP`.
   */
  async onModuleInit(): Promise<void> {
    if (!this.configService.telegram.setWebhookOnStartup) {
      this.logger.log(
        'Automatic webhook registration disabled (TELEGRAM_SET_WEBHOOK_ON_STARTUP=false)',
        TelegramApiService.name,
      );
      return;
    }

    try {
      await this.registerWebhook();
      await this.publishCommands();
      await this.verifyWebhook();
    } catch (error) {
      // Never let a startup webhook failure crash the whole application.
      this.logger.error(
        `${LogEvent.WebhookFailed}: startup registration failed`,
        error instanceof Error ? error.stack : String(error),
        TelegramApiService.name,
      );
    }
  }

  /** Register this service's webhook URL + secret token with Telegram. */
  async registerWebhook(): Promise<void> {
    await this.call('setWebhook', {
      url: this.webhookUrl(),
      secret_token: this.configService.telegram.webhookSecret,
      allowed_updates: ['message', 'edited_message', 'callback_query'],
      drop_pending_updates: false,
    });
    this.logger.log(`${LogEvent.WebhookRegistered}: ${this.webhookUrl()}`, TelegramApiService.name);
  }

  /**
   * Confirm Telegram accepted and can reach the webhook by reading back its
   * state via `getWebhookInfo`. Logs the registered URL, the pending-update
   * backlog and any delivery error Telegram last encountered.
   */
  async verifyWebhook(): Promise<TelegramWebhookInfo> {
    const info = await this.getWebhookInfo();
    const expected = this.webhookUrl();

    if (info.url !== expected) {
      this.logger.warn(
        `${LogEvent.WebhookFailed}: registered URL "${info.url}" does not match expected "${expected}"`,
        TelegramApiService.name,
      );
    }

    if (info.last_error_message) {
      this.logger.warn(
        `${LogEvent.WebhookFailed}: Telegram last delivery error — ${info.last_error_message}`,
        TelegramApiService.name,
      );
    }

    this.logger.log(
      `${LogEvent.WebhookVerified}: url=${info.url || '(none)'} pending=${info.pending_update_count} ip=${info.ip_address ?? 'n/a'}`,
      TelegramApiService.name,
    );
    return info;
  }

  /** Read the current webhook state from Telegram. */
  async getWebhookInfo(): Promise<TelegramWebhookInfo> {
    return this.call<TelegramWebhookInfo>('getWebhookInfo', {});
  }

  /** Publish the bot's command list so it appears in the Telegram UI menu. */
  async publishCommands(): Promise<void> {
    const commands: BotCommandDefinition[] = BOT_COMMAND_DESCRIPTIONS.map((entry) => ({
      command: entry.command,
      description: entry.description,
    }));
    await this.call('setMyCommands', { commands });
    this.logger.log(
      `${LogEvent.BotCommandsPublished}: ${commands.length} commands`,
      TelegramApiService.name,
    );
  }

  /** Fully-qualified webhook URL derived from configuration. */
  private webhookUrl(): string {
    const { baseUrl } = this.configService.app;
    const { webhookPath } = this.configService.telegram;
    return `${baseUrl.replace(/\/$/, '')}/${webhookPath}`;
  }

  async sendMessage(
    chatId: number,
    text: string,
    options: SendMessageOptions = {},
  ): Promise<TelegramMessage> {
    return this.call<TelegramMessage>('sendMessage', {
      chat_id: chatId,
      text,
      parse_mode: options.parse_mode ?? 'HTML',
      disable_web_page_preview: options.disable_web_page_preview ?? true,
      ...(options.reply_markup ? { reply_markup: options.reply_markup } : {}),
    });
  }

  async editMessageText(
    chatId: number,
    messageId: number,
    text: string,
    replyMarkup?: InlineKeyboardMarkup,
  ): Promise<void> {
    await this.call('editMessageText', {
      chat_id: chatId,
      message_id: messageId,
      text,
      parse_mode: 'HTML',
      disable_web_page_preview: true,
      ...(replyMarkup ? { reply_markup: replyMarkup } : {}),
    });
  }

  async sendLocation(
    chatId: number,
    latitude: number,
    longitude: number,
    options: SendLocationOptions = {},
  ): Promise<TelegramMessage> {
    return this.call<TelegramMessage>('sendLocation', {
      chat_id: chatId,
      latitude,
      longitude,
      ...(options.reply_markup ? { reply_markup: options.reply_markup } : {}),
    });
  }

  async answerCallbackQuery(
    callbackQueryId: string,
    options: AnswerCallbackQueryOptions = {},
  ): Promise<void> {
    await this.call('answerCallbackQuery', {
      callback_query_id: callbackQueryId,
      text: options.text,
      show_alert: options.show_alert ?? false,
    });
  }

  /**
   * Low-level Bot API invocation. Throws {@link TelegramApiException} on any
   * transport or API-level failure, with internal details logged but not leaked.
   */
  private async call<T>(method: string, payload: Record<string, unknown>): Promise<T> {
    try {
      const { data } = await this.http.post<TelegramApiResponse<T>>(`/${method}`, payload);
      if (!data.ok || data.result === undefined) {
        throw new TelegramApiException(
          `Telegram API "${method}" failed: ${data.description ?? 'unknown error'}`,
        );
      }
      return data.result;
    } catch (error) {
      if (error instanceof TelegramApiException) {
        this.logger.error(
          `${LogEvent.ApiError}: ${error.message}`,
          undefined,
          TelegramApiService.name,
        );
        throw error;
      }
      const description = isAxiosError(error)
        ? ((error.response?.data as { description?: string } | undefined)?.description ??
          error.message)
        : error instanceof Error
          ? error.message
          : 'unknown error';
      this.logger.error(
        `${LogEvent.ApiError}: Telegram "${method}" — ${description}`,
        error instanceof Error ? error.stack : undefined,
        TelegramApiService.name,
      );
      throw new TelegramApiException(`Telegram API "${method}" request failed`);
    }
  }
}
