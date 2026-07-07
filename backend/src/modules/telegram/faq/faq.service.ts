import { Inject, Injectable, LoggerService, OnModuleInit } from '@nestjs/common';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { FAQ_SOURCE, FaqSource } from './faq.source';
import { FaqItem } from './faq.model';

/**
 * Reusable FAQ access layer.
 *
 * Loads FAQ items from a swappable {@link FaqSource} and answers with:
 *   - {@link listItems}  all items (optionally by category)
 *   - {@link getItem}    one item by id
 *   - {@link findItems}  simple keyword matching (ranked; no AI / NLP / embeddings)
 *   - {@link matchItem}  the single best keyword match
 *
 * Keyword matching resolves multilingual terms (e.g. `delivery`, `shipping`,
 * `yetkazib berish`, `доставка`) to the same FAQ via the item's `keywords`.
 */
@Injectable()
export class FaqService implements OnModuleInit {
  private readonly items = new Map<string, FaqItem>();

  constructor(
    @Inject(FAQ_SOURCE) private readonly source: FaqSource,
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
  ) {}

  onModuleInit(): void {
    this.reload();
  }

  /** (Re)load all FAQ items from the source into the in-memory index. */
  reload(): void {
    this.items.clear();
    for (const item of this.source.load()) {
      this.items.set(item.id, item);
    }
    this.logger.log(`FAQ loaded: ${this.items.size} items`, FaqService.name);
  }

  /** List FAQ items, optionally filtered by category. */
  listItems(category?: string): FaqItem[] {
    return [...this.items.values()].filter((item) => !category || item.category === category);
  }

  /** Fetch a single FAQ item by id. */
  getItem(id: string): FaqItem | undefined {
    return this.items.get(id);
  }

  /** Keyword search: returns matching items, best match first. */
  findItems(query: string): FaqItem[] {
    const normalized = query.trim().toLowerCase();
    if (normalized.length === 0) {
      return [];
    }
    const tokens = normalized.split(/\s+/).filter((token) => token.length > 0);

    return [...this.items.values()]
      .map((item) => ({ item, score: this.score(item, normalized, tokens) }))
      .filter((entry) => entry.score > 0)
      .sort((a, b) => b.score - a.score)
      .map((entry) => entry.item);
  }

  /** Resolve a query to the single best-matching FAQ item, if any. */
  matchItem(query: string): FaqItem | undefined {
    return this.findItems(query)[0];
  }

  private score(item: FaqItem, normalizedQuery: string, tokens: string[]): number {
    let score = 0;
    // Whole-keyword phrase match (handles multi-word keywords like "yetkazib berish").
    for (const keyword of item.keywords) {
      if (normalizedQuery.includes(keyword)) {
        score += 3;
      }
    }
    // Token-level match against keywords + question text.
    const haystack =
      `${item.keywords.join(' ')} ${item.question_uz} ${item.question_ru}`.toLowerCase();
    for (const token of tokens) {
      if (haystack.includes(token)) {
        score += 1;
      }
    }
    return score;
  }
}
