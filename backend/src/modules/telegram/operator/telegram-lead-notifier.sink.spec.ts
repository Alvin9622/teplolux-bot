import { TelegramLeadNotifierSink } from './telegram-lead-notifier.sink';
import { OperatorSummaryBuilder } from './operator-summary.builder';
import { OperatorRequestSummary } from './operator-summary.types';

/** Single axios `post` mock shared by getChat + sendMessage across the suite. */
const post = jest.fn();
jest.mock('axios', () => ({
  __esModule: true,
  default: { create: (): { post: jest.Mock } => ({ post }) },
  isAxiosError: (e: unknown): boolean =>
    Boolean(e && (e as { isAxiosError?: boolean }).isAxiosError),
}));

/** Build a fake AxiosError with a Telegram error body. */
function axiosError(status: number, description: string, parameters?: object): unknown {
  return {
    isAxiosError: true,
    message: `Request failed with status code ${status}`,
    response: { status, data: { ok: false, description, ...(parameters ? { parameters } : {}) } },
  };
}

function summary(overrides: Partial<OperatorRequestSummary> = {}): OperatorRequestSummary {
  return {
    requestType: 'PRICE_REQUEST',
    customerName: 'Ali <Vali>',
    phone: '+998901234567',
    city: 'Toshkent shahri',
    customerMessage: 'Narx & shartlar',
    requestTime: '2026-07-09T10:00:00.000Z',
    language: 'uz',
    conversationFinishedAt: '2026-07-09T10:00:00.000Z',
    ...overrides,
  };
}

function makeLogger(): { log: jest.Mock; warn: jest.Mock; error: jest.Mock; debug: jest.Mock } {
  return { log: jest.fn(), warn: jest.fn(), error: jest.fn(), debug: jest.fn() };
}

function makeConfig(leadChatId: string): { telegram: { botToken: string; leadChatId: string } } {
  return { telegram: { botToken: '123:abc', leadChatId } };
}

/** Test sink whose retry backoff resolves instantly. */
class TestSink extends TelegramLeadNotifierSink {
  protected sleep(): Promise<void> {
    return Promise.resolve();
  }
}

function build(
  leadChatId: string,
  logger = makeLogger(),
): { sink: TestSink; logger: typeof logger } {
  const sink = new TestSink(
    makeConfig(leadChatId) as never,
    new OperatorSummaryBuilder(),
    logger as never,
  );
  return { sink, logger };
}

const okSend = { data: { ok: true, result: { message_id: 555 } } };

describe('TelegramLeadNotifierSink', () => {
  beforeEach(() => post.mockReset());

  describe('deliver', () => {
    it('sends the HTML-escaped summary to the configured chat id', async () => {
      post.mockResolvedValueOnce(okSend);
      const { sink, logger } = build('-1001234567890');

      await sink.deliver(summary());

      expect(post).toHaveBeenCalledTimes(1);
      const [method, payload] = post.mock.calls[0];
      expect(method).toBe('sendMessage');
      expect(payload.chat_id).toBe('-1001234567890');
      expect(payload.parse_mode).toBe('HTML');
      expect(payload.text).toContain('Ali &lt;Vali&gt;');
      expect(payload.text).toContain('Narx &amp; shartlar');
      expect(logger.error).not.toHaveBeenCalled();
    });

    it('surfaces the exact Telegram error and never throws on a 4xx failure', async () => {
      post.mockRejectedValueOnce(
        axiosError(403, 'Forbidden: bot is not a member of the group chat'),
      );
      const { sink, logger } = build('-1001234567890');

      await expect(sink.deliver(summary())).resolves.toBeUndefined();
      expect(post).toHaveBeenCalledTimes(1); // 4xx is NOT retried
      const msg = logger.error.mock.calls[0][0] as string;
      expect(msg).toContain('bot is not a member');
      expect(msg).toContain('Undelivered lead payload'); // lead preserved
    });

    it('retries a 429 (honoring retry_after) and then succeeds', async () => {
      post
        .mockRejectedValueOnce(axiosError(429, 'Too Many Requests', { retry_after: 1 }))
        .mockResolvedValueOnce(okSend);
      const { sink, logger } = build('-1001234567890');

      await sink.deliver(summary());

      expect(post).toHaveBeenCalledTimes(2);
      expect(logger.error).not.toHaveBeenCalled();
    });

    it('splits a message that exceeds the Telegram length limit', async () => {
      post.mockResolvedValue(okSend);
      const { sink } = build('-1001234567890');

      const huge = Array.from({ length: 2000 }, () => 'detail line').join('\n');
      await sink.deliver(summary({ customerMessage: huge }));

      expect(post.mock.calls.length).toBeGreaterThan(1);
      for (const [, payload] of post.mock.calls) {
        expect(payload.text.length).toBeLessThanOrEqual(4096);
      }
    });
  });

  describe('onModuleInit verification', () => {
    it('confirms reachability via getChat when enabled', async () => {
      post.mockResolvedValueOnce({
        data: { ok: true, result: { type: 'group', title: 'teplolux bot lead' } },
      });
      const { sink, logger } = build('-5411154154');

      await sink.onModuleInit();

      expect(post).toHaveBeenCalledWith('getChat', { chat_id: '-5411154154' });
      expect(logger.log.mock.calls.some(([m]) => String(m).includes('Lead Delivery Enabled'))).toBe(
        true,
      );
    });

    it('surfaces "chat not found" at startup without throwing', async () => {
      post.mockRejectedValueOnce(axiosError(400, 'Bad Request: chat not found'));
      const { sink, logger } = build('-5411154154');

      await expect(sink.onModuleInit()).resolves.toBeUndefined();
      const msg = logger.error.mock.calls[0][0] as string;
      expect(msg).toContain('chat not found');
      expect(msg).toContain('bot is a member');
    });

    it('detects a group→supergroup migration and names the new id', async () => {
      post.mockRejectedValueOnce(
        axiosError(400, 'Bad Request: group chat was upgraded to a supergroup chat', {
          migrate_to_chat_id: -1001111111111,
        }),
      );
      const { sink, logger } = build('-5411154154');

      await sink.onModuleInit();
      expect(logger.error.mock.calls[0][0]).toContain('-1001111111111');
    });

    it('loudly warns (and does not call Telegram) when delivery is disabled', async () => {
      const { sink, logger } = build('');

      await sink.onModuleInit();

      expect(post).not.toHaveBeenCalled();
      expect(
        logger.warn.mock.calls.some(([m]) => String(m).includes('Lead Delivery Disabled')),
      ).toBe(true);
    });
  });
});
