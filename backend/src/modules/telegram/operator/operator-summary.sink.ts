import { Inject, Injectable, LoggerService } from '@nestjs/common';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { LogEvent } from '../../../logger/log-events';
import { OperatorSummaryBuilder } from './operator-summary.builder';
import { OperatorRequestSummary } from './operator-summary.types';

/** DI token for the swappable {@link OperatorSummarySink}. */
export const OPERATOR_SUMMARY_SINK = Symbol('OPERATOR_SUMMARY_SINK');

/**
 * Destination for a generated operator summary.
 *
 * Kept behind an interface so the default logging sink can later be replaced by
 * a CRM sink (amoCRM, etc.) WITHOUT changing the builder, the service or the
 * conversation flow — just re-bind {@link OPERATOR_SUMMARY_SINK}.
 */
export interface OperatorSummarySink {
  deliver(summary: OperatorRequestSummary): Promise<void> | void;
}

/**
 * Default sink: logs the structured summary (readable block + JSON) and does
 * nothing else. No amoCRM, no operator chat — this is the CRM-ready seam.
 */
@Injectable()
export class LoggingOperatorSummarySink implements OperatorSummarySink {
  constructor(
    private readonly builder: OperatorSummaryBuilder,
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
  ) {}

  deliver(summary: OperatorRequestSummary): void {
    // Human-readable block for operators/observability.
    this.logger.log(
      `${LogEvent.OperatorSummaryGenerated}\n${this.builder.format(summary)}`,
      LoggingOperatorSummarySink.name,
    );
    // Structured object, ready for a future CRM integration to consume.
    this.logger.debug?.(JSON.stringify(summary), LoggingOperatorSummarySink.name);
  }
}
