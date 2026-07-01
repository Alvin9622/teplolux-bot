import { Module } from '@nestjs/common';
import { OperatorSummaryBuilder } from './operator-summary.builder';
import { OperatorSummaryService } from './operator-summary.service';
import { LoggingOperatorSummarySink, OPERATOR_SUMMARY_SINK } from './operator-summary.sink';

/**
 * Operator experience module.
 *
 * Provides the reusable {@link OperatorSummaryBuilder} and the
 * {@link OperatorSummaryService} facade, with the default logging sink bound to
 * {@link OPERATOR_SUMMARY_SINK}. To send summaries to a CRM later, replace only
 * the sink binding here — no changes to the conversation flow.
 */
@Module({
  providers: [
    OperatorSummaryBuilder,
    { provide: OPERATOR_SUMMARY_SINK, useClass: LoggingOperatorSummarySink },
    OperatorSummaryService,
  ],
  exports: [OperatorSummaryService, OperatorSummaryBuilder],
})
export class OperatorModule {}
