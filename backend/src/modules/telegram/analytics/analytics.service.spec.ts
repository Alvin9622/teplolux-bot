import { CallbackData } from '../constants/callback-data.constants';
import { FlowAction } from '../conversation/conversation.constants';
import { AnalyticsService, SESSION_IDLE_MS } from './analytics.service';
import { AnalyticsActor, AnalyticsEvent, AnalyticsEventPayload } from './analytics.event';
import { AnalyticsSink } from './analytics.sink';

const logger = { log: jest.fn(), warn: jest.fn(), debug: jest.fn() } as never;

/** Capturing sink so tests can assert on emitted events synchronously. */
class RecordingSink implements AnalyticsSink {
  readonly events: AnalyticsEventPayload[] = [];
  record(event: AnalyticsEventPayload): void {
    this.events.push(event);
  }
}

const actor: AnalyticsActor = { telegramUserId: BigInt(42), language: 'uz' };

function names(sink: RecordingSink): string[] {
  return sink.events.map((e) => e.eventName);
}

describe('AnalyticsService', () => {
  let sink: RecordingSink;
  let service: AnalyticsService;

  beforeEach(() => {
    sink = new RecordingSink();
    service = new AnalyticsService(sink, logger);
  });

  it('builds a consistent event payload with all required fields', () => {
    service.track(AnalyticsEvent.BotStarted, actor);

    // First event opens a session, so BotStarted is the second emitted event.
    const started = sink.events.find((e) => e.eventName === AnalyticsEvent.BotStarted);
    expect(started).toBeDefined();
    expect(started?.telegramUserId).toBe('42');
    expect(started?.language).toBe('uz');
    expect(typeof started?.timestamp).toBe('string');
    expect(Number.isNaN(Date.parse(started!.timestamp))).toBe(false);
    expect(started?.sessionId).toEqual(expect.any(String));
    expect(started?.sessionId.length).toBeGreaterThan(0);
  });

  it('preserves supplied metadata and drops undefined values', () => {
    service.track(AnalyticsEvent.ProductCategoryViewed, actor, {
      selectedProduct: 'boilers',
      requestType: 'PRICE_REQUEST',
      city: undefined,
    });

    const event = sink.events.find((e) => e.eventName === AnalyticsEvent.ProductCategoryViewed);
    expect(event?.metadata).toEqual({ selectedProduct: 'boilers', requestType: 'PRICE_REQUEST' });
    expect(event?.metadata).not.toHaveProperty('city');
  });

  it('opens one session and reuses its id across events', () => {
    service.track(AnalyticsEvent.BotStarted, actor);
    service.track(AnalyticsEvent.MainMenuViewed, actor);

    expect(names(sink)).toEqual([
      AnalyticsEvent.SessionStarted,
      AnalyticsEvent.BotStarted,
      AnalyticsEvent.MainMenuViewed,
    ]);
    const ids = new Set(sink.events.map((e) => e.sessionId));
    expect(ids.size).toBe(1);
  });

  it('ends the session and starts a new one after the idle timeout', () => {
    jest.useFakeTimers();
    try {
      service.track(AnalyticsEvent.BotStarted, actor);
      const firstSession = sink.events[0].sessionId;

      jest.advanceTimersByTime(SESSION_IDLE_MS + 1);
      service.track(AnalyticsEvent.MainMenuViewed, actor);

      const ended = sink.events.find((e) => e.eventName === AnalyticsEvent.SessionEnded);
      expect(ended).toBeDefined();
      expect(ended?.sessionId).toBe(firstSession);
      expect(ended?.metadata?.eventCount).toBe(1);
      expect(typeof ended?.metadata?.durationSeconds).toBe('number');

      // A fresh session id is issued for activity after the timeout.
      const menu = sink.events.find((e) => e.eventName === AnalyticsEvent.MainMenuViewed);
      expect(menu?.sessionId).not.toBe(firstSession);
    } finally {
      jest.useRealTimers();
    }
  });

  it('resolves menu callbacks to their semantic events', () => {
    service.trackMenu(actor, CallbackData.Service);
    service.trackMenu(actor, CallbackData.Boilers);
    service.trackMenu(actor, CallbackData.SelectLangRu);

    const events = sink.events.filter((e) => e.eventName !== AnalyticsEvent.SessionStarted);
    expect(events[0]).toMatchObject({ eventName: AnalyticsEvent.ServiceClicked });
    expect(events[1]).toMatchObject({
      eventName: AnalyticsEvent.RequestPriceClicked,
      metadata: { selectedProduct: 'boilers' },
    });
    expect(events[2]).toMatchObject({
      eventName: AnalyticsEvent.LanguageSelected,
      metadata: { selectedLanguage: 'ru' },
    });
  });

  it('ignores flow-control callbacks (owned by the conversation engine)', () => {
    service.trackMenu(actor, FlowAction.Submit);
    service.trackMenu(actor, FlowAction.Cancel);
    service.trackMenu(actor, 'totally:unknown');

    expect(sink.events).toHaveLength(0);
  });

  it('maps flow phases to canonical flow events', () => {
    service.trackFlow(actor, 'started', { flowId: 'contact_request' });
    service.trackFlow(actor, 'completed');

    const events = names(sink).filter((n) => n !== AnalyticsEvent.SessionStarted);
    expect(events).toEqual([
      AnalyticsEvent.ContactFlowStarted,
      AnalyticsEvent.ContactFlowCompleted,
    ]);
  });

  it('never throws when the sink fails, and does not break the caller', () => {
    const failingSink: AnalyticsSink = {
      record: jest.fn(() => {
        throw new Error('sink down');
      }),
    };
    const resilient = new AnalyticsService(failingSink, logger);

    expect(() => resilient.track(AnalyticsEvent.BotStarted, actor)).not.toThrow();
    expect(failingSink.record).toHaveBeenCalled();
  });

  it('swallows rejected async sink deliveries', async () => {
    const asyncSink: AnalyticsSink = {
      record: jest.fn().mockRejectedValue(new Error('async fail')),
    };
    const resilient = new AnalyticsService(asyncSink, logger);

    expect(() => resilient.track(AnalyticsEvent.BotStarted, actor)).not.toThrow();
    await Promise.resolve();
    expect(asyncSink.record).toHaveBeenCalled();
  });
});
