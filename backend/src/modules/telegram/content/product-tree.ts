import { Locale } from '../../../i18n/i18n.types';
import { contentPageCallback } from './content.constants';
import { ProductConfigNode, PRODUCTS_CONFIG } from './products.config';

/**
 * A node in the in-memory Product Tree, built from {@link PRODUCTS_CONFIG}.
 *
 * The tree is DATA — categories/subcategories live in the configuration, never
 * hardcoded here. A node with `children` is an intermediate level; a node
 * without children is a leaf that opens an action page (or, when `contentPageId`
 * is set, reuses an existing rich content page).
 */
export interface ProductNode {
  /** Stable id, unique across the tree (used in callbacks). No `:` characters. */
  readonly id: string;
  /** Localised titles (from config). */
  readonly title_uz: string;
  readonly title_ru: string;
  /** Optional localised descriptions shown on a level / action page. */
  readonly description_uz?: string;
  readonly description_ru?: string;
  /** Optional emoji/icon prefixed to the title. */
  readonly icon?: string;
  /** Parent node id (root has none) — used to resolve ◀ Back. */
  readonly parentId?: string;
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

/** Root node id — the "Products" entry point (from config). */
export const PRODUCT_ROOT_ID = PRODUCTS_CONFIG.id;

/**
 * Build the in-memory tree from the configuration: drop hidden nodes, sort each
 * level by `sortOrder`, and derive each child's `parentId`. Pure data transform
 * — the navigator is unaware of the source, so config can later come from
 * teplolux.uz / a DB without any consumer change.
 */
function buildNode(raw: ProductConfigNode, parentId?: string): ProductNode {
  const children = (raw.children ?? [])
    .filter((child) => child.isVisible !== false)
    .slice()
    .sort((a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0))
    .map((child) => buildNode(child, raw.id));
  return {
    id: raw.id,
    title_uz: raw.title_uz,
    title_ru: raw.title_ru,
    description_uz: raw.description_uz,
    description_ru: raw.description_ru,
    icon: raw.icon,
    parentId: raw.parentId ?? parentId,
    websiteUrl: raw.websiteUrl,
    catalogUrl: raw.catalogUrl,
    contentPageId: raw.contentPageId,
    priceTrigger: raw.priceTrigger,
    children: children.length > 0 ? children : undefined,
  };
}

/** Build a Product Tree from a configuration node (defaults to the shipped one). */
export function buildProductTree(config: ProductConfigNode = PRODUCTS_CONFIG): ProductNode {
  return buildNode(config);
}

/** The shipped Product Tree, loaded from {@link PRODUCTS_CONFIG}. */
export const PRODUCT_TREE: ProductNode = buildProductTree();

/** Resolve a node's display title for a locale (icon + localised title). */
export function nodeTitle(node: ProductNode, locale: Locale): string {
  const title = locale === 'ru' ? node.title_ru : node.title_uz;
  return node.icon ? `${node.icon} ${title}` : title;
}

/** Resolve a node's localised description ('' when none). */
export function nodeDescription(node: ProductNode, locale: Locale): string {
  return (locale === 'ru' ? node.description_ru : node.description_uz) ?? '';
}

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
