/**
 * A single FAQ entry, parsed from a structured Markdown file.
 *
 * The Markdown files are the editable source of truth for answers, so no answer
 * text is hardcoded in handlers.
 */
export interface FaqItem {
  /** Stable id derived from the file name, e.g. `delivery`. */
  readonly id: string;
  readonly question: string;
  readonly answer: string;
  readonly category: string;
  /** Match keywords (multilingual), e.g. `delivery`, `yetkazib berish`, `доставка`. */
  readonly keywords: ReadonlyArray<string>;
}

/** Default category for FAQ items without an explicit one. */
export const FAQ_DEFAULT_CATEGORY = 'general';
