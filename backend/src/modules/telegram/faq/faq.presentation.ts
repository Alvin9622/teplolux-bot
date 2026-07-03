/**
 * Telegram presentation vocabulary for the FAQ module.
 *
 * Callback payloads are namespaced under `faq:` so they never collide with menu,
 * flow or content callbacks. This file carries ONLY presentation concerns — the
 * FAQ data and matching stay in {@link FaqService}; nothing is duplicated.
 */

export const FaqAction = {
  /** `faq:list:<scope>` opens the FAQ list for a scope. */
  ListPrefix: 'faq:list:',
  /** `faq:item:<scope>:<id>` opens a single FAQ answer. */
  ItemPrefix: 'faq:item:',
} as const;

export function faqListCallback(scope: string): string {
  return `${FaqAction.ListPrefix}${scope}`;
}

export function faqItemCallback(scope: string, id: string): string {
  return `${FaqAction.ItemPrefix}${scope}:${id}`;
}

/**
 * Product category scopes (match the product content-page id suffixes, e.g.
 * `product_boilers`). Opening the FAQ from a product page uses one of these.
 */
export const PRODUCT_FAQ_SCOPES: ReadonlyArray<string> = [
  'boilers',
  'radiators',
  'floor_heating',
  'water_heaters',
  'pumps',
];

/**
 * The curated, product-relevant FAQ items shown for a product scope — referenced
 * by their existing {@link FaqService} ids (delivery / payment / warranty /
 * service). No FAQ content is duplicated; only the selection lives here.
 */
export const PRODUCT_FAQ_IDS: ReadonlyArray<string> = [
  'delivery',
  'payment',
  'warranty',
  'service',
];

/** True when a scope is a product category (vs. a plain FAQ category). */
export function isProductScope(scope: string): boolean {
  return PRODUCT_FAQ_SCOPES.includes(scope);
}
