import { Inject, Injectable, LoggerService } from '@nestjs/common';
import axios, { AxiosInstance, isAxiosError } from 'axios';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { AppConfigService } from '../../../config/app-config.service';
import { LogEvent } from '../../../logger/log-events';
import { escapeHtml } from '../constants/messages.constants';
import { OperatorSummaryBuilder } from './operator-summary.builder';
import { OperatorSummarySink } from './operator-summary.sink';
import { OperatorRequestSummary } from './operator-summary.types';

const TELEGRAM_API_BASE = 'https://api.telegram.org';
const DELIVERY_TIMEOUT_MS = 10_000;

/**
 * Sink that forwards every generated lead summary to a Telegram group or
 * channel, so the sales team receives each request in real time.
 *
 * Delivery is best-effort: the readable summary is always logged first (keeping
 * the observability the logging sink provided), and a failed Telegram send is
 * logged but NEVER thrown — a notification error must not break the customer
 * conversation. Bound only when `TELEGRAM_LEAD_CHAT_ID` is configured (see
 * {@link OperatorModule}); otherwise the logging-only sink is used.
 */
@Injectable()
export class TelegramLeadNotifierSink implements OperatorSummarySink {
  private readonly http: AxiosInstance;
  private readonly chatId: string;

  constructor(
    configService: AppConfigService,
    private readonly builder: OperatorSummaryBuilder,
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
  ) {
    const { botToken, leadChatId } = configService.telegram;
    this.chatId = leadChatId;
    this.http = axios.create({
      baseURL: `${TELEGRAM_API_BASE}/bot${botToken}`,
      timeout: DELIVERY_TIMEOUT_MS,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  async deliver(summary: OperatorRequestSummary): Promise<void> {
    const block = this.builder.format(summary);

    // Always keep the observable log line (same behaviour as the logging sink).
    this.logger.log(
      `${LogEvent.OperatorSummaryGenerated}\n${block}`,
      TelegramLeadNotifierSink.name,
    );

    try {
      // Wrap the (plain-text) summary in <pre> after escaping so any characters
      // in customer input can never break Telegram's HTML parser.
      await this.http.post('sendMessage', {
        chat_id: this.chatId,
        text: `<b>📩 Yangi lead / Новый лид</b>\n<pre>${escapeHtml(block)}</pre>`,
        parse_mode: 'HTML',
        disable_web_page_preview: true,
      });
      this.logger.log(
        `${LogEvent.LeadNotificationSent}: chat=${this.chatId}`,
        TelegramLeadNotifierSink.name,
      );
    } catch (error) {
      const detail = isAxiosError(error)
        ? `${error.response?.status ?? ''} ${JSON.stringify(error.response?.data ?? error.message)}`
        : error instanceof Error
          ? error.message
          : String(error);
      this.logger.error(
        `${LogEvent.LeadNotificationFailed}: chat=${this.chatId} — ${detail}`,
        error instanceof Error ? error.stack : undefined,
        TelegramLeadNotifierSink.name,
      );
    }
  }
}
