import { Inject, Injectable, LoggerService } from '@nestjs/common';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { LogEvent } from '../../../logger/log-events';
import { AnalyticsEventPayload } from './analytics.event';

/** DI token for the swappable {@link AnalyticsSink}. */
export const ANALYTICS_SINK = Symbol('ANALYTICS_SINK');

/**
 * Destination for a tracked analytics event.
 *
 * This is the provider-independent seam: today the default sink writes to the
 * existing logging infrastructure, but a Google Analytics / PostHog / Mixpanel
 * / BigQuery / Power BI sink can replace the binding WITHOUT touching
 * {@link AnalyticsService} or any Telegram handler — just re-bind
 * {@link ANALYTICS_SINK}. `record` may be async; the service never awaits it,
 * so a slow or failing sink can never block or break a bot response.
 */
export interface AnalyticsSink {
  record(event: AnalyticsEventPayload): Promise<void> | void;
}

/**
 * Default sink: emits the event through the shared logger (readable name +
 * structured JSON). No external analytics service — this is the pluggable seam
 * a real provider replaces later.
 */
@Injectable()
export class LoggingAnalyticsSink implements AnalyticsSink {
  constructor(@Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService) {}

  record(event: AnalyticsEventPayload): void {
    this.logger.log(
      `${LogEvent.AnalyticsEventTracked}: ${event.eventName}`,
      LoggingAnalyticsSink.name,
    );
    // Structured record, ready for a future provider/pipeline to consume.
    this.logger.debug?.(JSON.stringify(event), LoggingAnalyticsSink.name);
  }
}
