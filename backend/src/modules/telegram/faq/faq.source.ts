import { join } from 'node:path';
import { Inject, Injectable, LoggerService } from '@nestjs/common';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { loadMarkdownDocs, markdownFirstHeading, parseCsvList } from '../markdown/markdown-loader';
import { FAQ_DEFAULT_CATEGORY, FaqItem } from './faq.model';

/** DI token for the swappable {@link FaqSource}. */
export const FAQ_SOURCE = Symbol('FAQ_SOURCE');

/**
 * A source of FAQ items.
 *
 * Kept behind an interface so the Markdown-file source used today can later be
 * replaced by a database / CMS source WITHOUT changing {@link FaqService} or any
 * consumer.
 */
export interface FaqSource {
  load(): FaqItem[];
}

/**
 * Loads FAQ items from structured Markdown files under `./articles`, reusing the
 * shared {@link loadMarkdownDocs} loader. Each file maps: front-matter
 * `question` (or first heading) → question, body → answer, `category` and
 * comma-separated `keywords`.
 */
@Injectable()
export class MarkdownFaqSource implements FaqSource {
  private readonly baseDir = join(__dirname, 'articles');

  constructor(@Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService) {}

  load(): FaqItem[] {
    return loadMarkdownDocs(this.baseDir, this.logger).map((doc) => ({
      id: doc.slug,
      question: doc.meta.question ?? markdownFirstHeading(doc.body) ?? this.humanize(doc.slug),
      answer: doc.body.trim(),
      category: doc.meta.category || doc.folderCategory || FAQ_DEFAULT_CATEGORY,
      keywords: parseCsvList(doc.meta.keywords),
    }));
  }

  /** Turn a slug like `working-hours` into a readable `Working Hours` fallback. */
  private humanize(slug: string): string {
    return slug
      .split('/')
      .pop()!
      .replace(/[-_]/g, ' ')
      .replace(/\b\w/g, (char) => char.toUpperCase());
  }
}
