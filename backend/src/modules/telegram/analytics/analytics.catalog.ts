/**
 * Maps raw Telegram callback payloads to semantic analytics events.
 *
 * Keeping this mapping here (rather than sprinkling `analytics.track(...)` calls
 * across every handler) means the informational/navigation handlers stay
 * untouched: the central dispatcher records one interaction per callback and
 * this catalog decides what it means. Flow triggers and flow-control callbacks
 * are intentionally NOT listed — the {@link ConversationService} owns the
 * precise flow-lifecycle events, so listing them here would double-count.
 */
import { CallbackData } from '../constants/callback-data.constants';
import { ContentAction } from '../content/content.constants';
import { PnavAction, PRODUCT_ROOT_ID } from '../content/product-tree';
import { FaqAction } from '../faq/faq.presentation';
import { AnalyticsEvent, AnalyticsMetadata } from './analytics.event';

export interface ResolvedInteraction {
  readonly eventName: string;
  readonly metadata?: AnalyticsMetadata;
}

/** Product category codes keyed by their catalog callback / content slug. */
const PRODUCT_BY_CATEGORY_CALLBACK: Readonly<Record<string, string>> = {
  [CallbackData.Boilers]: 'boilers',
  [CallbackData.Radiators]: 'radiators',
  [CallbackData.FloorHeating]: 'floor_heating',
  [CallbackData.WaterHeaters]: 'water_heaters',
  [CallbackData.Pumps]: 'pumps',
};

/** Exact-match callbacks that map straight to an event. */
const EXACT_INTERACTIONS: Readonly<Record<string, ResolvedInteraction>> = {
  // Lead intents (the flow itself is tracked separately by ConversationService).
  [CallbackData.Service]: { eventName: AnalyticsEvent.ServiceClicked },
  [CallbackData.Dealer]: { eventName: AnalyticsEvent.DealerClicked },
  [CallbackData.Operator]: { eventName: AnalyticsEvent.OperatorClicked },
  // Navigation / information.
  [CallbackData.BackToMenu]: { eventName: AnalyticsEvent.MainMenuViewed },
  [CallbackData.Contact]: { eventName: AnalyticsEvent.ContactsViewed },
  [CallbackData.Location]: {
    eventName: AnalyticsEvent.MenuItemClicked,
    metadata: { item: 'location' },
  },
  [CallbackData.ChangeLanguage]: {
    eventName: AnalyticsEvent.MenuItemClicked,
    metadata: { item: 'change_language' },
  },
  [CallbackData.SelectLangUz]: {
    eventName: AnalyticsEvent.LanguageSelected,
    metadata: { selectedLanguage: 'uz' },
  },
  [CallbackData.SelectLangRu]: {
    eventName: AnalyticsEvent.LanguageSelected,
    metadata: { selectedLanguage: 'ru' },
  },
};

/** Content pages that carry a specific analytics meaning. */
const CONTENT_PAGE_INTERACTIONS: Readonly<Record<string, ResolvedInteraction>> = {
  about: { eventName: AnalyticsEvent.AboutCompanyViewed },
  contacts: { eventName: AnalyticsEvent.ContactsViewed },
  products: { eventName: AnalyticsEvent.CatalogOpened },
  product_boilers: {
    eventName: AnalyticsEvent.ProductCategoryViewed,
    metadata: { selectedProduct: 'boilers' },
  },
  product_radiators: {
    eventName: AnalyticsEvent.ProductCategoryViewed,
    metadata: { selectedProduct: 'radiators' },
  },
  product_floor_heating: {
    eventName: AnalyticsEvent.ProductCategoryViewed,
    metadata: { selectedProduct: 'floor_heating' },
  },
  product_water_heaters: {
    eventName: AnalyticsEvent.ProductCategoryViewed,
    metadata: { selectedProduct: 'water_heaters' },
  },
  product_pumps: {
    eventName: AnalyticsEvent.ProductCategoryViewed,
    metadata: { selectedProduct: 'pumps' },
  },
};

/**
 * Resolve a callback payload to its analytics event, or `null` when the
 * callback is a flow trigger / flow control (owned elsewhere) or is unknown.
 */
export function resolveCallbackInteraction(data: string): ResolvedInteraction | null {
  // Catalog category buttons start a price request — record the click intent.
  const product = PRODUCT_BY_CATEGORY_CALLBACK[data];
  if (product) {
    return {
      eventName: AnalyticsEvent.RequestPriceClicked,
      metadata: { selectedProduct: product },
    };
  }

  const exact = EXACT_INTERACTIONS[data];
  if (exact) {
    return exact;
  }

  if (data.startsWith(ContentAction.PagePrefix)) {
    const pageId = data.slice(ContentAction.PagePrefix.length);
    return (
      CONTENT_PAGE_INTERACTIONS[pageId] ?? {
        eventName: AnalyticsEvent.MenuItemClicked,
        metadata: { page: pageId },
      }
    );
  }

  // Product Navigator: the root is a catalog open; deeper nodes are category views.
  if (data.startsWith(PnavAction.Prefix)) {
    const rest = data.slice(PnavAction.Prefix.length);
    const nodeId = rest.split(':')[0];
    return nodeId === PRODUCT_ROOT_ID
      ? { eventName: AnalyticsEvent.CatalogOpened }
      : { eventName: AnalyticsEvent.ProductCategoryViewed, metadata: { node: nodeId } };
  }

  // Opening an FAQ list (from a product page or elsewhere) is a FAQ view.
  if (data.startsWith(FaqAction.ListPrefix)) {
    return {
      eventName: AnalyticsEvent.FaqViewed,
      metadata: { scope: data.slice(FaqAction.ListPrefix.length) },
    };
  }

  return null;
}
