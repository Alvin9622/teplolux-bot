import { Inject, Injectable, LoggerService, OnModuleInit } from '@nestjs/common';
import axios, { AxiosInstance, isAxiosError } from 'axios';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { AppConfigService } from '../../../config/app-config.service';
import { LogEvent } from '../../../logger/log-events';
import { escapeHtml } from '../constants/messages.constants';
import { TelegramApiResponse, TelegramChat, TelegramMessage } from '../types/telegram-api.types';
import { OperatorSummaryBuilder } from './operator-summary.builder';
import { OperatorSummarySink } from './operator-summary.sink';
import { OperatorRequestSummary } from './operator-summary.types';

const TELEGRAM_API_BASE = 'https://api.telegram.org';
const DELIVERY_TIMEOUT_MS = 10_000;
/** Telegram hard limit for a text message. */
const TELEGRAM_MAX_LEN = 4096;
/** Total send attempts (1 initial + retries) for transient failures. */
const MAX_ATTEMPTS = 3;
const BASE_BACKOFF_MS = 500;

/** Shape of a Telegram Bot API error body (HTTP 4xx/5xx). */
interface TelegramErrorBody {
  ok: false;
  error_code?: number;
  description?: string;
  parameters?: { retry_after?: number; migrate_to_chat_id?: number };
}

/** Classification of a failed send used to decide retry vs. surface. */
interface FailureInfo {
  retryable: boolean;
  retryAfterMs?: number;
  errorCode?: number;
  migrateTo?: number;
  message: string;
}

/**
 * Sink that forwards every generated lead summary to a Telegram group/channel,
 * so the sales team receives each request in real time.
 *
 * Hardened for production:
 *  - Startup verification (`getChat`) surfaces "chat not found", "bot is not a
 *    member", wrong-token and group→supergroup migration BEFORE the first lead.
 *  - Rich, non-swallowing logs at every stage (sending → delivered / failed with
 *    the EXACT Telegram error).
 *  - Retries transient failures (429 with `retry_after`, 5xx, network) with
 *    backoff; never retries deterministic 4xx (bad chat / no permission).
 *  - Splits messages longer than Telegram's 4096-char limit.
 *  - Never throws and never loses a lead: on final failure the full payload is
 *    logged so it can be recovered.
 *
 * Bound only when `TELEGRAM_LEAD_CHAT_ID` is configured (see {@link OperatorModule});
 * otherwise the logging-only sink is used — but this sink still logs, at startup,
 * WHY delivery is disabled so the silent-failure trap is impossible.
 */
@Injectable()
export class TelegramLeadNotifierSink implements OperatorSummarySink, OnModuleInit {
  private readonly http: AxiosInstance;
  private readonly chatId: string;

  constructor(
    configService: AppConfigService,
    private readonly builder: OperatorSummaryBuilder,
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
  ) {
    const { botToken, leadChatId } = configService.telegram;
    this.chatId = leadChatId.trim();
    this.http = axios.create({
      baseURL: `${TELEGRAM_API_BASE}/bot${botToken}`,
      timeout: DELIVERY_TIMEOUT_MS,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  /**
   * Verify configuration and reachability at boot so misconfiguration is loud
   * and immediate instead of a silently-dropped lead later. Never throws — a
   * verification failure must not stop the app from starting.
   */
  async onModuleInit(): Promise<void> {
    if (!this.chatId) {
      this.logger.warn(
        `${LogEvent.LeadDeliveryDisabled}: TELEGRAM_LEAD_CHAT_ID is not set — leads will be logged only, not delivered to a Telegram group. Set it (e.g. -1001234567890) and redeploy to enable delivery.`,
        TelegramLeadNotifierSink.name,
      );
      return;
    }

    if (!/^(-?\d+|@[\w]{5,})$/.test(this.chatId)) {
      this.logger.warn(
        `${LogEvent.LeadDeliveryVerifyFailed}: TELEGRAM_LEAD_CHAT_ID="${this.chatId}" is not a valid chat id. Use a numeric id (e.g. -1001234567890) or @channelusername.`,
        TelegramLeadNotifierSink.name,
      );
      // Continue: still attempt delivery so the real Telegram error is surfaced.
    }

    try {
      const { data } = await this.http.post<TelegramApiResponse<TelegramChat>>('getChat', {
        chat_id: this.chatId,
      });
      const chat = data.result;
      this.logger.log(
        `${LogEvent.LeadDeliveryEnabled}: chat=${this.chatId} type=${chat?.type ?? '?'} title=${chat?.title ?? chat?.username ?? '?'}`,
        TelegramLeadNotifierSink.name,
      );
    } catch (error) {
      const info = this.classify(error);
      this.logger.error(
        `${LogEvent.LeadDeliveryVerifyFailed}: cannot reach chat=${this.chatId} — ${info.message}. ` +
          `Check that the bot is a member of the group (or admin of the channel), the id is correct, and TELEGRAM_BOT_TOKEN matches the bot in the group.` +
          (info.migrateTo
            ? ` The group was upgraded to a supergroup — update TELEGRAM_LEAD_CHAT_ID to ${info.migrateTo}.`
            : ''),
        undefined,
        TelegramLeadNotifierSink.name,
      );
    }
  }

  async deliver(summary: OperatorRequestSummary): Promise<void> {
    const block = this.builder.format(summary);

    // Always keep the observable payload log (recoverable even if delivery dies).
    this.logger.log(
      `${LogEvent.OperatorSummaryGenerated}\n${block}`,
      TelegramLeadNotifierSink.name,
    );

    if (!this.chatId) {
      // Should not happen (this sink is only bound when configured), but guard.
      this.logger.warn(
        `${LogEvent.LeadDeliveryDisabled}: no chat id configured; lead was logged only.`,
        TelegramLeadNotifierSink.name,
      );
      return;
    }

    const messages = this.buildMessages(block);
    this.logger.log(
      `${LogEvent.LeadDeliverySending}: chat=${this.chatId} parts=${messages.length}`,
      TelegramLeadNotifierSink.name,
    );

    try {
      for (const text of messages) {
        const sent = await this.sendWithRetry(text);
        this.logger.log(
          `${LogEvent.LeadNotificationSent}: chat=${this.chatId} message_id=${sent.message_id}`,
          TelegramLeadNotifierSink.name,
        );
      }
    } catch (error) {
      const info = this.classify(error);
      // Surface the EXACT Telegram error and keep the full payload for recovery.
      this.logger.error(
        `${LogEvent.LeadNotificationFailed}: chat=${this.chatId} — ${info.message}` +
          (info.migrateTo ? ` (group migrated to supergroup ${info.migrateTo})` : '') +
          `\nUndelivered lead payload:\n${block}`,
        error instanceof Error ? error.stack : undefined,
        TelegramLeadNotifierSink.name,
      );
    }
  }

  /** POST sendMessage, retrying transient failures (429/5xx/network) with backoff. */
  private async sendWithRetry(text: string): Promise<TelegramMessage> {
    let lastError: unknown;
    for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
      try {
        const { data } = await this.http.post<TelegramApiResponse<TelegramMessage>>('sendMessage', {
          chat_id: this.chatId,
          text,
          parse_mode: 'HTML',
          disable_web_page_preview: true,
        });
        if (!data.ok || !data.result) {
          throw new Error(data.description ?? 'Telegram returned ok=false');
        }
        return data.result;
      } catch (error) {
        lastError = error;
        const info = this.classify(error);
        if (!info.retryable || attempt === MAX_ATTEMPTS) {
          throw error;
        }
        const wait = info.retryAfterMs ?? BASE_BACKOFF_MS * attempt;
        this.logger.warn(
          `${LogEvent.LeadNotificationFailed}: transient error (attempt ${attempt}/${MAX_ATTEMPTS}), retrying in ${wait}ms — ${info.message}`,
          TelegramLeadNotifierSink.name,
        );
        await this.sleep(wait);
      }
    }
    throw lastError;
  }

  /**
   * Build the outbound message(s): the summary is HTML-escaped and wrapped in
   * <pre> so any customer input is safe, and split across multiple messages if
   * it would exceed Telegram's length limit.
   */
  private buildMessages(block: string): string[] {
    const header = '<b>📩 Yangi lead / Новый лид</b>';
    const wrap = (body: string, withHeader: boolean): string =>
      `${withHeader ? `${header}\n` : ''}<pre>${escapeHtml(body)}</pre>`;

    if (wrap(block, true).length <= TELEGRAM_MAX_LEN) {
      return [wrap(block, true)];
    }

    // Split by lines into chunks that each stay under the limit.
    const messages: string[] = [];
    const lines = block.split('\n');
    let chunk = '';
    let first = true;
    for (const line of lines) {
      const candidate = chunk ? `${chunk}\n${line}` : line;
      if (wrap(candidate, first).length > TELEGRAM_MAX_LEN && chunk) {
        messages.push(wrap(chunk, first));
        first = false;
        chunk = line;
      } else {
        chunk = candidate;
      }
    }
    if (chunk) {
      messages.push(wrap(chunk, first));
    }
    return messages;
  }

  /** Interpret a failed request into a retry decision + human-readable reason. */
  private classify(error: unknown): FailureInfo {
    if (isAxiosError(error)) {
      const status = error.response?.status;
      const body = error.response?.data as TelegramErrorBody | undefined;
      const description = body?.description ?? error.message;
      const retryAfter = body?.parameters?.retry_after;
      const migrateTo = body?.parameters?.migrate_to_chat_id;
      // No response → network/timeout: retryable.
      if (!error.response) {
        return { retryable: true, message: `network error: ${error.message}` };
      }
      if (status === 429) {
        return {
          retryable: true,
          retryAfterMs: retryAfter ? retryAfter * 1000 : undefined,
          errorCode: 429,
          message: `rate limited${retryAfter ? ` (retry after ${retryAfter}s)` : ''}: ${description}`,
        };
      }
      if (status && status >= 500) {
        return {
          retryable: true,
          errorCode: status,
          message: `Telegram ${status}: ${description}`,
        };
      }
      // Deterministic 4xx (400 chat not found / bad request, 403 forbidden): do not retry.
      return {
        retryable: false,
        errorCode: status,
        migrateTo,
        message: `Telegram ${status ?? '4xx'}: ${description}`,
      };
    }
    return { retryable: false, message: error instanceof Error ? error.message : String(error) };
  }

  /** Overridable in tests so retries do not wait in real time. */
  protected sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
