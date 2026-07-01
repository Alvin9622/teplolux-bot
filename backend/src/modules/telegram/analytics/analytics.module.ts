import { Module } from '@nestjs/common';
import { AnalyticsService } from './analytics.service';
import { ANALYTICS_SINK, LoggingAnalyticsSink } from './analytics.sink';

/**
 * Analytics & event-tracking module.
 *
 * Provides the reusable {@link AnalyticsService} with the default logging sink
 * bound to {@link ANALYTICS_SINK}. To ship events to a real provider later
 * (Google Analytics, PostHog, Mixpanel, BigQuery, Power BI) replace only the
 * sink binding here — the Telegram handlers stay unchanged.
 */
@Module({
  providers: [{ provide: ANALYTICS_SINK, useClass: LoggingAnalyticsSink }, AnalyticsService],
  exports: [AnalyticsService],
})
export class AnalyticsModule {}
