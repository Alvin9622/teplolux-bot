import { Inject, Injectable } from '@nestjs/common';
import { OperatorSummaryBuilder } from './operator-summary.builder';
import { OPERATOR_SUMMARY_SINK, OperatorSummarySink } from './operator-summary.sink';
import { OperatorRequestSummary, OperatorSummaryInput } from './operator-summary.types';

/**
 * Facade used by flows to record a submitted request as an operator summary.
 *
 * Builds the structured summary (via {@link OperatorSummaryBuilder}) and hands
 * it to the configured {@link OperatorSummarySink} (logging today, CRM later),
 * returning the object so callers/future CRM code can consume it.
 */
@Injectable()
export class OperatorSummaryService {
  constructor(
    private readonly builder: OperatorSummaryBuilder,
    @Inject(OPERATOR_SUMMARY_SINK) private readonly sink: OperatorSummarySink,
  ) {}

  async record(input: OperatorSummaryInput): Promise<OperatorRequestSummary> {
    const summary = this.builder.build(input);
    await this.sink.deliver(summary);
    return summary;
  }
}
