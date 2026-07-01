/**
 * A single knowledge-base article, parsed from a structured Markdown file.
 *
 * The Markdown files are the reusable, editable source of truth for long-form
 * content (company info, delivery, warranty, product/brand descriptions), so
 * this text never has to be hardcoded inside handlers.
 */
export interface KnowledgeArticle {
  /** Stable id derived from the file path, e.g. `company`, `products/boilers`. */
  readonly slug: string;
  /** Top-level folder (`products`, `brands`) or `general` for root articles. */
  readonly category: string;
  /** Human-readable title (front-matter `title`, first heading, or the slug). */
  readonly title: string;
  /** Optional keywords (front-matter `tags`) used by `findArticle`. */
  readonly tags: ReadonlyArray<string>;
  /** The Markdown body (front-matter stripped). */
  readonly content: string;
}

/** Lightweight article descriptor without the (potentially large) body. */
export type KnowledgeArticleSummary = Omit<KnowledgeArticle, 'content'>;

/** Default category for articles that live at the knowledge-base root. */
export const GENERAL_CATEGORY = 'general';
