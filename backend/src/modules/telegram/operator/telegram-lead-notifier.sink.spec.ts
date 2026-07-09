import { TelegramLeadNotifierSink } from './telegram-lead-notifier.sink';
import { OperatorSummaryBuilder } from './operator-summary.builder';
import { OperatorRequestSummary } from './operator-summary.types';

/** Captures the axios instance the sink creates so we can assert/stub `.post`. */
const post = jest.fn();
jest.mock('axios', () => ({
  __esModule: true,
  default: { create: (): { post: jest.Mock } => ({ post }) },
  isAxiosError: (): boolean => false,
}));

function summary(): OperatorRequestSummary {
  return {
    requestType: 'PRICE_REQUEST',
    customerName: 'Ali <Vali>',
    phone: '+998901234567',
    city: 'Toshkent',
    customerMessage: 'Narx & shartlar',
    requestTime: '2026-07-09T10:00:00.000Z',
    language: 'uz',
    conversationFinishedAt: '2026-07-09T10:00:00.000Z',
  };
}

function makeLogger(): { log: jest.Mock; error: jest.Mock; debug: jest.Mock } {
  return { log: jest.fn(), error: jest.fn(), debug: jest.fn() };
}

function makeConfig(leadChatId: string): { telegram: { botToken: string; leadChatId: string } } {
  return { telegram: { botToken: '123:abc', leadChatId } };
}

describe('TelegramLeadNotifierSink', () => {
  beforeEach(() => post.mockReset());

  it('sends the escaped summary to the configured chat id', async () => {
    const logger = makeLogger();
    post.mockResolvedValueOnce({ data: { ok: true } });
    const sink = new TelegramLeadNotifierSink(
      makeConfig('-1001234567890') as never,
      new OperatorSummaryBuilder(),
      logger as never,
    );

    await sink.deliver(summary());

    expect(post).toHaveBeenCalledTimes(1);
    const [method, payload] = post.mock.calls[0];
    expect(method).toBe('sendMessage');
    expect(payload.chat_id).toBe('-1001234567890');
    expect(payload.parse_mode).toBe('HTML');
    // Customer input is HTML-escaped so it can never break Telegram's parser.
    expect(payload.text).toContain('Ali &lt;Vali&gt;');
    expect(payload.text).toContain('Narx &amp; shartlar');
    expect(logger.error).not.toHaveBeenCalled();
  });

  it('never throws when Telegram delivery fails', async () => {
    const logger = makeLogger();
    post.mockRejectedValueOnce(new Error('network down'));
    const sink = new TelegramLeadNotifierSink(
      makeConfig('-1001234567890') as never,
      new OperatorSummaryBuilder(),
      logger as never,
    );

    await expect(sink.deliver(summary())).resolves.toBeUndefined();
    expect(logger.error).toHaveBeenCalledTimes(1);
  });
});
