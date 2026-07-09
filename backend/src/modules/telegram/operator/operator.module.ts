import { Module } from '@nestjs/common';
import { AppConfigService } from '../../../config/app-config.service';
import { OperatorSummaryBuilder } from './operator-summary.builder';
import { OperatorSummaryService } from './operator-summary.service';
import {
  LoggingOperatorSummarySink,
  OperatorSummarySink,
  OPERATOR_SUMMARY_SINK,
} from './operator-summary.sink';
import { TelegramLeadNotifierSink } from './telegram-lead-notifier.sink';

/**
 * Operator experience module.
 *
 * Provides the reusable {@link OperatorSummaryBuilder} and the
 * {@link OperatorSummaryService} facade. The active {@link OPERATOR_SUMMARY_SINK}
 * is chosen at runtime: when `TELEGRAM_LEAD_CHAT_ID` is configured, leads are
 * delivered to that Telegram group/channel; otherwise they are only logged.
 * Both sinks stay behind the same interface, so the conversation flow is
 * unaffected and a CRM sink can replace them later without touching the flow.
 */
@Module({
  providers: [
    OperatorSummaryBuilder,
    LoggingOperatorSummarySink,
    TelegramLeadNotifierSink,
    {
      provide: OPERATOR_SUMMARY_SINK,
      inject: [AppConfigService, TelegramLeadNotifierSink, LoggingOperatorSummarySink],
      useFactory: (
        config: AppConfigService,
        telegramSink: TelegramLeadNotifierSink,
        loggingSink: LoggingOperatorSummarySink,
      ): OperatorSummarySink => (config.telegram.leadChatId ? telegramSink : loggingSink),
    },
    OperatorSummaryService,
  ],
  exports: [OperatorSummaryService, OperatorSummaryBuilder],
})
export class OperatorModule {}
