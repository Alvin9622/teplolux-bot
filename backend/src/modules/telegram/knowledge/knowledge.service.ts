import { Inject, Injectable, LoggerService, OnModuleInit } from '@nestjs/common';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { KNOWLEDGE_SOURCE, KnowledgeSource } from './markdown-knowledge.source';
import { KnowledgeArticle, KnowledgeArticleSummary } from './knowledge.types';

/**
 * Reusable knowledge-base access layer.
 *
 * Loads structured articles from a swappable {@link KnowledgeSource} and exposes
 * a small, intent-revealing API so Telegram pages/handlers can read long-form
 * content instead of hardcoding it:
 *   - {@link getArticle}   fetch one article by slug
 *   - {@link listArticles} list article summaries (optionally by category)
 *   - {@link findArticle}  keyword search (no AI/vectors — future-swappable)
 *
 * The keyword `findArticle` is deliberately simple; a future AI/semantic search
 * can replace it (or the underlying source) without changing consumers.
 */
@Injectable()
export class KnowledgeService implements OnModuleInit {
  private readonly index = new Map<string, KnowledgeArticle>();

  constructor(
    @Inject(KNOWLEDGE_SOURCE) private readonly source: KnowledgeSource,
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
  ) {}

  onModuleInit(): void {
    this.reload();
  }

  /** (Re)load all articles from the source into the in-memory index. */
  reload(): void {
    this.index.clear();
    for (const article of this.source.load()) {
      this.index.set(article.slug, article);
    }
    this.logger.log(`Knowledge base loaded: ${this.index.size} articles`, KnowledgeService.name);
  }

  /** Fetch a single article by its slug (e.g. `products/boilers`). */
  getArticle(slug: string): KnowledgeArticle | undefined {
    return this.index.get(slug);
  }

  /** List article summaries, optionally filtered by category. */
  listArticles(category?: string): KnowledgeArticleSummary[] {
    const articles = [...this.index.values()].filter(
      (article) => !category || article.category === category,
    );
    return articles.map(({ content: _content, ...summary }) => summary);
  }

  /**
   * Keyword search across slug, title, tags and body. Ranks by the number of
   * query tokens matched (title/tag hits weigh more than body hits).
   */
  findArticle(query: string): KnowledgeArticleSummary[] {
    const tokens = query
      .toLowerCase()
      .split(/\s+/)
      .map((token) => token.trim())
      .filter((token) => token.length > 0);
    if (tokens.length === 0) {
      return [];
    }

    const scored = [...this.index.values()]
      .map((article) => ({ article, score: this.score(article, tokens) }))
      .filter((entry) => entry.score > 0)
      .sort((a, b) => b.score - a.score);

    return scored.map(({ article: { content: _content, ...summary } }) => summary);
  }

  private score(article: KnowledgeArticle, tokens: string[]): number {
    const haystackStrong =
      `${article.slug} ${article.title} ${article.tags.join(' ')}`.toLowerCase();
    const haystackBody = article.content.toLowerCase();
    let score = 0;
    for (const token of tokens) {
      if (haystackStrong.includes(token)) {
        score += 2;
      } else if (haystackBody.includes(token)) {
        score += 1;
      }
    }
    return score;
  }
}
