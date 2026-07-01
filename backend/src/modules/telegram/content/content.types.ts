import { TranslationKey } from '../../../i18n/i18n.types';
import { CompanyConfig } from '../config/company-config.types';

/**
 * A button action on a content page. Discriminated by `type` so the renderer
 * maps each to the right Telegram button (callback vs url) and the service
 * knows how to react. This is the full set required by the product spec.
 */
export type ContentButtonAction =
  | { readonly type: 'page'; readonly pageId: string } // open another content page
  | { readonly type: 'flow'; readonly trigger: string } // start a conversation flow (trigger callback)
  | { readonly type: 'url'; readonly url: string } // open a website
  | { readonly type: 'phone'; readonly phone: string } // reveal a callable phone number
  | { readonly type: 'callback'; readonly data: string } // reuse an existing callback handler (e.g. Location)
  | { readonly type: 'back' } // go to the page's parent (or main menu)
  | { readonly type: 'mainMenu' }; // return to the main menu

/** A single labelled button; the label is always a translation key. */
export interface ContentButton {
  readonly labelKey: TranslationKey;
  readonly action: ContentButtonAction;
}

/**
 * A declarative, translatable informational page. All copy is referenced by
 * i18n keys — never inlined — so the same structure serves every page and
 * language. Reusable for About, Contacts, Branches, Warranty, Products, etc.
 */
export interface ContentPage {
  readonly id: string;
  readonly titleKey: TranslationKey;
  readonly descriptionKey: TranslationKey;
  /** Optional image (photo URL) rendered above the text. */
  readonly imageUrl?: string;
  /** Parent page id used to resolve the ⬅ Back button (root pages omit it). */
  readonly parentId?: string;
  /**
   * Optional resolver mapping the company configuration to `{{placeholder}}`
   * values interpolated into the title/description — so pages read business
   * facts from configuration instead of hardcoding them in the i18n catalogs.
   */
  readonly descriptionParams?: (config: CompanyConfig) => Record<string, string | number>;
  /** Inline keyboard layout, as rows of buttons. */
  readonly buttons: ReadonlyArray<ReadonlyArray<ContentButton>>;
}
