import { CatalogCategoryId } from '../content/catalog.config';

/**
 * Structured, reusable company configuration consumed by the bot.
 *
 * Groups all business information behind a single shape so pages and handlers
 * never reference hardcoded strings. The concrete values are provided by a
 * swappable source (static today; database / admin panel / CMS later).
 */
export interface CompanyInfo {
  readonly name: string;
}

export interface ContactInfo {
  readonly phone: string;
  readonly email: string;
  readonly website: string;
  readonly address: string;
}

export interface SocialLinks {
  readonly telegram: string;
  readonly instagram: string;
  readonly facebook: string;
  readonly youtube: string;
}

export interface CompanyConfig {
  readonly company: CompanyInfo;
  readonly contacts: ContactInfo;
  readonly social: SocialLinks;
  readonly workingHours: string;
  /** Per-category catalog URLs (reuses the existing catalog configuration). */
  readonly catalog: Readonly<Record<CatalogCategoryId, string>>;
}
