/**
 * Per-category product catalog URLs.
 *
 * A single, configurable source of truth for "View Catalog" links so URLs are
 * never hardcoded inside handlers or page definitions. Swap these placeholders
 * for real catalog links (or load them from configuration/env) as catalogs
 * mature; the structure is reusable for any future catalog category.
 */
export const CatalogCategory = {
  Boilers: 'boilers',
  Radiators: 'radiators',
  FloorHeating: 'floorHeating',
  WaterHeaters: 'waterHeaters',
  Pumps: 'pumps',
} as const;

export type CatalogCategoryId = (typeof CatalogCategory)[keyof typeof CatalogCategory];

/** Configurable catalog URL per product category. */
export const CATALOG_URLS: Readonly<Record<CatalogCategoryId, string>> = {
  boilers: 'https://teplolux.example.com/catalog/boilers',
  radiators: 'https://teplolux.example.com/catalog/radiators',
  floorHeating: 'https://teplolux.example.com/catalog/floor-heating',
  waterHeaters: 'https://teplolux.example.com/catalog/water-heaters',
  pumps: 'https://teplolux.example.com/catalog/pumps',
};

/** Resolve the catalog URL for a category. */
export function catalogUrl(category: CatalogCategoryId): string {
  return CATALOG_URLS[category];
}
