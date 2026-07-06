import { TranslationKey } from '../../../i18n/i18n.types';
import { TKey } from '../../../i18n/i18n.keys';
import { CallbackData } from '../constants/callback-data.constants';
import { CATALOG_URLS, CatalogCategory } from './catalog.config';
import { ContentPageId, contentPageCallback } from './content.constants';

/**
 * A node in the reusable Product Tree.
 *
 * The tree is the single, declarative source of truth for the Product Navigator
 * — categories/subcategories are DATA, never hardcoded pages. A node with
 * `children` is an intermediate level; a node without children is a leaf that
 * opens an action page (or, when `contentPageId` is set, reuses an existing
 * rich content page).
 */
export interface ProductNode {
  /** Stable id, unique across the tree (used in callbacks). No `:` characters. */
  readonly id: string;
  /** Localised title (i18n key). */
  readonly titleKey: TranslationKey;
  /** Parent node id (root has none) — used to resolve ◀ Back. */
  readonly parentId?: string;
  /** Optional short description (i18n key) shown on the level/action page. */
  readonly descriptionKey?: TranslationKey;
  /** Optional "View on Website" URL. May stay empty (architecture only). */
  readonly websiteUrl?: string;
  /** Optional "Catalog" URL. May stay empty (architecture only). */
  readonly catalogUrl?: string;
  /** Child nodes; presence means "open the next level" instead of an action page. */
  readonly children?: ReadonlyArray<ProductNode>;
  /**
   * Leaf only: reuse an existing content page (e.g. the rich Product Experience
   * Center page) instead of the generic action page. Its button links straight
   * to the existing `content:page:*` callback.
   */
  readonly contentPageId?: string;
  /** Leaf action page only: reuse an existing Request Price flow trigger. */
  readonly priceTrigger?: string;
}

/** Maximum categories shown per page before pagination kicks in. */
export const PRODUCT_NAV_PAGE_SIZE = 6;

/** Root node id — the "Products" entry point. */
export const PRODUCT_ROOT_ID = 'products';

/** Build a top-level category leaf that reuses an existing product content page. */
function category(
  id: string,
  titleKey: TranslationKey,
  contentPageId: string,
  priceTrigger: string,
  catalogUrl: string,
): ProductNode {
  return { id, titleKey, parentId: PRODUCT_ROOT_ID, contentPageId, priceTrigger, catalogUrl };
}

/**
 * The shipped Product Tree.
 *
 * Today the five categories are leaves that reuse the existing rich product
 * pages (no page is replaced). The structure already supports subcategories and
 * >6 children with pagination — add nodes here to grow it; no code changes.
 */
export const PRODUCT_TREE: ProductNode = {
  id: PRODUCT_ROOT_ID,
  titleKey: TKey.contentProductsTitle,
  descriptionKey: TKey.contentProductsDescription,
  children: [
    category(
      'boilers',
      TKey.contentProductBoilersTitle,
      ContentPageId.ProductBoilers,
      CallbackData.Boilers,
      CATALOG_URLS[CatalogCategory.Boilers],
    ),
    category(
      'radiators',
      TKey.contentProductRadiatorsTitle,
      ContentPageId.ProductRadiators,
      CallbackData.Radiators,
      CATALOG_URLS[CatalogCategory.Radiators],
    ),
    category(
      'floor_heating',
      TKey.contentProductFloorHeatingTitle,
      ContentPageId.ProductFloorHeating,
      CallbackData.FloorHeating,
      CATALOG_URLS[CatalogCategory.FloorHeating],
    ),
    category(
      'water_heaters',
      TKey.contentProductWaterHeatersTitle,
      ContentPageId.ProductWaterHeaters,
      CallbackData.WaterHeaters,
      CATALOG_URLS[CatalogCategory.WaterHeaters],
    ),
    category(
      'pumps',
      TKey.contentProductPumpsTitle,
      ContentPageId.ProductPumps,
      CallbackData.Pumps,
      CATALOG_URLS[CatalogCategory.Pumps],
    ),
  ],
};

/** Depth-first lookup of a node by id (small tree — linear is fine). */
export function findProductNode(
  id: string,
  node: ProductNode = PRODUCT_TREE,
): ProductNode | undefined {
  if (node.id === id) {
    return node;
  }
  for (const child of node.children ?? []) {
    const found = findProductNode(id, child);
    if (found) {
      return found;
    }
  }
  return undefined;
}

/** True when a node opens the next navigation level (vs. an action page). */
export function hasChildren(node: ProductNode): boolean {
  return (node.children?.length ?? 0) > 0;
}

/** Number of pages needed to show `total` items at the given page size. */
export function productPageCount(total: number, size = PRODUCT_NAV_PAGE_SIZE): number {
  return Math.max(1, Math.ceil(total / size));
}

/** Clamp a requested page index into range and return that page's slice. */
export function productPageSlice<T>(
  items: ReadonlyArray<T>,
  page: number,
  size = PRODUCT_NAV_PAGE_SIZE,
): { readonly page: number; readonly pages: number; readonly items: T[] } {
  const pages = productPageCount(items.length, size);
  const clamped = Math.min(Math.max(page, 0), pages - 1);
  const start = clamped * size;
  return { page: clamped, pages, items: items.slice(start, start + size) };
}

// ---------------------------------------------------------------------------
// Callbacks — namespaced under `pnav:` so they never collide with menu / flow /
// content / faq callbacks. `pnav:<id>` opens a node; `pnav:<id>:<page>` paginates.
// ---------------------------------------------------------------------------

export const PnavAction = { Prefix: 'pnav:' } as const;

export function pnavCallback(nodeId: string, page = 0): string {
  return page > 0 ? `${PnavAction.Prefix}${nodeId}:${page}` : `${PnavAction.Prefix}${nodeId}`;
}

/** Parse a `pnav:` callback into a node id + page, or null when not a pnav callback. */
export function parsePnav(data: string): { nodeId: string; page: number } | null {
  if (!data.startsWith(PnavAction.Prefix)) {
    return null;
  }
  const rest = data.slice(PnavAction.Prefix.length);
  const sep = rest.indexOf(':');
  if (sep === -1) {
    return { nodeId: rest, page: 0 };
  }
  const page = Number.parseInt(rest.slice(sep + 1), 10);
  return { nodeId: rest.slice(0, sep), page: Number.isFinite(page) ? page : 0 };
}

/** The callback a child button points to: existing content page, or a tree level. */
export function childCallback(child: ProductNode): string {
  if (!hasChildren(child) && child.contentPageId) {
    return contentPageCallback(child.contentPageId);
  }
  return pnavCallback(child.id);
}
