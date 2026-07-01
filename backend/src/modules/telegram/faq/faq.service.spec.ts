import { FaqService } from './faq.service';
import { MarkdownFaqSource } from './faq.source';

const logger = { log: jest.fn(), warn: jest.fn() } as never;

function buildService(): FaqService {
  const service = new FaqService(new MarkdownFaqSource(logger), logger);
  service.onModuleInit();
  return service;
}

describe('FaqService', () => {
  let service: FaqService;

  beforeEach(() => {
    service = buildService();
  });

  it('loads the FAQ items from the markdown files', () => {
    const all = service.listItems();
    expect(all.length).toBe(7);
    expect(all.some((item) => item.id === 'delivery')).toBe(true);
  });

  it('getItem returns a parsed item (question, answer, category, keywords)', () => {
    const delivery = service.getItem('delivery');
    expect(delivery).toBeDefined();
    expect(delivery?.question).toBe('How does delivery work?');
    expect(delivery?.category).toBe('orders');
    expect(delivery?.keywords).toContain('delivery');
    expect(delivery?.answer).toContain('deliver');
    // Front-matter must be stripped from the answer.
    expect(delivery?.answer.startsWith('---')).toBe(false);
  });

  it('getItem returns undefined for an unknown id', () => {
    expect(service.getItem('does-not-exist')).toBeUndefined();
  });

  it('listItems can filter by category', () => {
    expect(
      service
        .listItems('orders')
        .map((i) => i.id)
        .sort(),
    ).toEqual(['delivery', 'payment']);
    expect(service.listItems('service').map((i) => i.id)).toEqual(['service']);
  });

  it('resolves multilingual keywords to the same Delivery FAQ', () => {
    for (const query of ['delivery', 'shipping', 'yetkazib berish', 'доставка']) {
      expect(service.matchItem(query)?.id).toBe('delivery');
    }
  });

  it('resolves keywords for other topics', () => {
    expect(service.matchItem('kafolat')?.id).toBe('warranty');
    expect(service.matchItem('время работы')?.id).toBe('working-hours');
    expect(service.matchItem('диллер / diler')?.id).toBe('dealer');
  });

  it('returns nothing for empty or unmatched queries', () => {
    expect(service.findItems('')).toEqual([]);
    expect(service.findItems('zzzznotarealtoken')).toEqual([]);
  });
});
