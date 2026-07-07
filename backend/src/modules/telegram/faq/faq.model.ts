import { Locale } from '../../../i18n/i18n.types';

/**
 * A single FAQ entry, parsed from a structured Markdown file.
 *
 * The Markdown files are the editable source of truth for answers, so no answer
 * text is hardcoded in handlers. Questions and answers are bilingual (uz/ru) —
 * the customer interface never shows English.
 */
export interface FaqItem {
  /** Stable id derived from the file name, e.g. `delivery`. */
  readonly id: string;
  /** Localised question texts. */
  readonly question_uz: string;
  readonly question_ru: string;
  /** Localised answer texts. */
  readonly answer_uz: string;
  readonly answer_ru: string;
  readonly category: string;
  /** Match keywords (multilingual), e.g. `delivery`, `yetkazib berish`, `доставка`. */
  readonly keywords: ReadonlyArray<string>;
}

/** Default category for FAQ items without an explicit one. */
export const FAQ_DEFAULT_CATEGORY = 'general';

/** Resolve the localised question for a locale. */
export function faqQuestion(item: FaqItem, locale: Locale): string {
  return locale === 'ru' ? item.question_ru : item.question_uz;
}

/** Resolve the localised answer for a locale. */
export function faqAnswer(item: FaqItem, locale: Locale): string {
  return locale === 'ru' ? item.answer_ru : item.answer_uz;
}
