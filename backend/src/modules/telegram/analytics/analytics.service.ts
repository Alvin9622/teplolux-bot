import { randomUUID } from 'crypto';
import { Inject, Injectable, LoggerService } from '@nestjs/common';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { LogEvent } from '../../../logger/log-events';
import {
  AnalyticsActor,
  AnalyticsEvent,
  AnalyticsEventPayload,
  AnalyticsMetadata,
  FLOW_PHASE_EVENT,
  FlowPhase,
} from './analytics.event';
import { resolveCallbackInteraction } from './analytics.catalog';
import { ANALYTICS_SINK, AnalyticsSink } from './analytics.sink';

/** A session ends after this much inactivity; the next event starts a new one. */
export const SESSION_IDLE_MS = 30 * 60 * 1000;

interface SessionRecord {
  sessionId: string;
  startedAt: number;
  lastActivityAt: number;
  eventCount: number;
}

/**
 * Reusable, provider-independent analytics facade.
 *
 * Every important user interaction becomes a consistent {@link AnalyticsEventPayload}
 * (eventName, telegramUserId, language, timestamp, sessionId, optional metadata)
 * and is handed to the configured {@link AnalyticsSink}. Tracking is fire-and-forget:
 * it is synchronous for the caller, never awaited, and fully guarded — a slow or
 * throwing sink can never block a Telegram response or break the bot.
 *
 * Sessions are tracked in-memory here (no database, per the current stage): the
 * first event for a user opens a session (emitting {@link AnalyticsEvent.SessionStarted}),
 * and the next event after {@link SESSION_IDLE_MS} of inactivity closes it
 * (emitting {@link AnalyticsEvent.SessionEnded} with the duration).
 */
@Injectable()
export class AnalyticsService {
  private readonly sessions = new Map<string, SessionRecord>();

  constructor(
    @Inject(ANALYTICS_SINK) private readonly sink: AnalyticsSink,
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
  ) {}

  /** Core primitive: record one event for an actor. Never throws. */
  track(eventName: string, actor: AnalyticsActor, metadata?: AnalyticsMetadata): void {
    try {
      const session = this.resolveSession(actor);
      session.eventCount += 1;
      this.dispatch(this.build(eventName, actor, session.sessionId, metadata));
    } catch (error) {
      this.onError(error);
    }
  }

  /**
   * Record a menu/navigation interaction from its raw callback payload. The
   * catalog resolves the semantic event; unknown or flow-owned callbacks are
   * silently ignored so nothing is double-counted.
   */
  trackMenu(actor: AnalyticsActor, callbackData: string, metadata?: AnalyticsMetadata): void {
    const resolved = resolveCallbackInteraction(callbackData);
    if (!resolved) {
      return;
    }
    this.track(resolved.eventName, actor, { ...resolved.metadata, ...metadata });
  }

  /** Record a guided-conversation lifecycle event (started/step/back/…). */
  trackFlow(actor: AnalyticsActor, phase: FlowPhase, metadata?: AnalyticsMetadata): void {
    this.track(FLOW_PHASE_EVENT[phase], actor, metadata);
  }

  /** Record an informational page view (About, Contacts, FAQ, …). */
  trackPage(actor: AnalyticsActor, eventName: string, metadata?: AnalyticsMetadata): void {
    this.track(eventName, actor, metadata);
  }

  // -------------------------------------------------------------------------
  // Sessions
  // -------------------------------------------------------------------------

  private resolveSession(actor: AnalyticsActor): SessionRecord {
    const key = String(actor.telegramUserId);
    const now = Date.now();
    let session = this.sessions.get(key);

    if (session && now - session.lastActivityAt > SESSION_IDLE_MS) {
      this.endSession(key, session, actor);
      session = undefined;
    }

    if (!session) {
      session = { sessionId: randomUUID(), startedAt: now, lastActivityAt: now, eventCount: 0 };
      this.sessions.set(key, session);
      this.dispatch(this.build(AnalyticsEvent.SessionStarted, actor, session.sessionId));
    }

    session.lastActivityAt = now;
    return session;
  }

  private endSession(key: string, session: SessionRecord, actor: AnalyticsActor): void {
    this.sessions.delete(key);
    const durationMs = Date.now() - session.startedAt;
    this.dispatch(
      this.build(AnalyticsEvent.SessionEnded, actor, session.sessionId, {
        durationMs,
        durationSeconds: Math.round(durationMs / 1000),
        eventCount: session.eventCount,
      }),
    );
  }

  // -------------------------------------------------------------------------
  // Helpers
  // -------------------------------------------------------------------------

  private build(
    eventName: string,
    actor: AnalyticsActor,
    sessionId: string,
    metadata?: AnalyticsMetadata,
  ): AnalyticsEventPayload {
    const cleaned = metadata ? this.clean(metadata) : undefined;
    return {
      eventName,
      telegramUserId: String(actor.telegramUserId),
      language: actor.language,
      timestamp: new Date().toISOString(),
      sessionId,
      ...(cleaned && Object.keys(cleaned).length > 0 ? { metadata: cleaned } : {}),
    };
  }

  /** Drop `undefined` values so the payload stays clean for any store. */
  private clean(metadata: AnalyticsMetadata): AnalyticsMetadata {
    const out: AnalyticsMetadata = {};
    for (const [key, value] of Object.entries(metadata)) {
      if (value !== undefined) {
        out[key] = value;
      }
    }
    return out;
  }

  /** Hand the event to the sink without awaiting it; swallow any failure. */
  private dispatch(event: AnalyticsEventPayload): void {
    try {
      const result = this.sink.record(event);
      if (result && typeof (result as Promise<void>).then === 'function') {
        (result as Promise<void>).catch((error) => this.onError(error));
      }
    } catch (error) {
      this.onError(error);
    }
  }

  private onError(error: unknown): void {
    const message = error instanceof Error ? error.message : String(error);
    // Analytics must never affect the user experience — log and move on.
    this.logger.warn(`${LogEvent.AnalyticsTrackingFailed}: ${message}`, AnalyticsService.name);
  }
}
