import { KnowledgeService } from './knowledge.service';
import { KnowledgeArticleSummary } from './knowledge.types';
import { MarkdownKnowledgeSource } from './markdown-knowledge.source';

const logger = { log: jest.fn(), warn: jest.fn() } as never;

function buildService(): KnowledgeService {
  const service = new KnowledgeService(new MarkdownKnowledgeSource(logger), logger);
  service.onModuleInit();
  return service;
}

describe('KnowledgeService', () => {
  let service: KnowledgeService;

  beforeEach(() => {
    service = buildService();
  });

  it('loads the structured markdown articles (root + products + brands)', () => {
    const all = service.listArticles();
    // 6 root + 5 products + 4 brands.
    expect(all.length).toBeGreaterThanOrEqual(15);
    expect(all.some((a) => a.slug === 'products/boilers')).toBe(true);
    expect(all.some((a) => a.slug === 'brands/tesy')).toBe(true);
  });

  it('getArticle returns a parsed article (title, tags, category, content)', () => {
    const company = service.getArticle('company');
    expect(company).toBeDefined();
    expect(company?.title).toBe('About Teplolux');
    expect(company?.category).toBe('general');
    expect(company?.tags).toContain('company');
    expect(company?.content).toContain('Teplolux');
    // Front-matter must be stripped from the body.
    expect(company?.content.startsWith('---')).toBe(false);
  });

  it('getArticle resolves nested slugs with their folder as category', () => {
    const boilers = service.getArticle('products/boilers');
    expect(boilers?.category).toBe('products');
    expect(boilers?.title).toBe('Boilers');
  });

  it('getArticle returns undefined for an unknown slug', () => {
    expect(service.getArticle('does-not-exist')).toBeUndefined();
  });

  it('listArticles filters by category and omits the body', () => {
    expect(service.listArticles('products')).toHaveLength(5);
    expect(service.listArticles('brands')).toHaveLength(4);

    const [summary] = service.listArticles('brands');
    expect((summary as KnowledgeArticleSummary & { content?: string }).content).toBeUndefined();
  });

  it('findArticle performs keyword search and ranks the best match first', () => {
    expect(service.findArticle('warranty')[0].slug).toBe('warranty');
    expect(service.findArticle('boiler').some((a) => a.slug === 'products/boilers')).toBe(true);
    expect(service.findArticle('delivery').some((a) => a.slug === 'delivery')).toBe(true);
  });

  it('findArticle returns nothing for empty or unmatched queries', () => {
    expect(service.findArticle('')).toEqual([]);
    expect(service.findArticle('zzzznotarealtoken')).toEqual([]);
  });
});
