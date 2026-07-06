import { CallbackData } from '../constants/callback-data.constants';
import { CATALOG_URLS, CatalogCategory } from './catalog.config';
import { ContentPageId } from './content.constants';

/**
 * Single, reusable Product configuration — the source of truth for the whole
 * Product Navigator. Add / re-order / hide categories and subcategories HERE;
 * no code (and never ProductNavigatorService) needs to change. See PRODUCTS.md.
 *
 * The structure is intentionally plain data (nested `children`), so it can later
 * be generated from teplolux.uz or loaded from a JSON/DB source and fed to
 * {@link buildProductTree} without touching any consumer.
 */
export interface ProductConfigNode {
  /** Stable, unique id used in callbacks. Must not contain `:`. */
  readonly id: string;
  /** Localised titles (shown as the button / page title). */
  readonly title_uz: string;
  readonly title_ru: string;
  /** Optional localised descriptions (shown on a level / action page). */
  readonly description_uz?: string;
  readonly description_ru?: string;
  /** Optional emoji/icon prefixed to the title. */
  readonly icon?: string;
  /** Optional "View on Website" URL. Leave empty until real URLs exist. */
  readonly websiteUrl?: string;
  /** Optional "Catalog" URL. */
  readonly catalogUrl?: string;
  /** Explicit parent id; normally derived from nesting, override only if needed. */
  readonly parentId?: string;
  /** Child nodes — presence turns a node into an intermediate navigation level. */
  readonly children?: ReadonlyArray<ProductConfigNode>;
  /** Hidden when `false` (kept in config but not shown). Defaults to visible. */
  readonly isVisible?: boolean;
  /** Ascending sort within a level. Defaults to 0. */
  readonly sortOrder?: number;
  /**
   * Optional reuse hooks — a leaf may open an existing rich content page and/or
   * start the existing Request Price flow, instead of the generic action page.
   */
  readonly contentPageId?: string;
  readonly priceTrigger?: string;
}

/**
 * The shipped configuration.
 *
 * Today the five categories are leaves that reuse the existing product pages
 * (nothing replaced). `websiteUrl` is intentionally empty (no real URLs yet);
 * `catalogUrl` reuses the existing catalog configuration. Grow this tree to
 * 1000+ products / 100+ subcategories / any depth — the navigator adapts with
 * no code changes.
 */
export const PRODUCTS_CONFIG: ProductConfigNode = {
  id: 'products',
  icon: '🏠',
  title_uz: 'Mahsulotlar',
  title_ru: 'Продукция',
  description_uz: 'Quyidagi mahsulot toifalaridan birini tanlang:',
  description_ru: 'Выберите одну из категорий продукции:',
  children: [
    {
      id: 'boilers',
      icon: '🔥',
      title_uz: 'Kotyollar',
      title_ru: 'Котлы',
      isVisible: true,
      sortOrder: 10,
      websiteUrl: '',
      catalogUrl: CATALOG_URLS[CatalogCategory.Boilers],
      contentPageId: ContentPageId.ProductBoilers,
      priceTrigger: CallbackData.Boilers,
    },
    {
      id: 'radiators',
      icon: '♨️',
      title_uz: 'Radiatorlar',
      title_ru: 'Радиаторы',
      isVisible: true,
      sortOrder: 20,
      websiteUrl: '',
      catalogUrl: CATALOG_URLS[CatalogCategory.Radiators],
      contentPageId: ContentPageId.ProductRadiators,
      priceTrigger: CallbackData.Radiators,
    },
    {
      id: 'floor_heating',
      icon: '🌡',
      title_uz: 'Issiq pol',
      title_ru: 'Тёплый пол',
      isVisible: true,
      sortOrder: 30,
      websiteUrl: '',
      catalogUrl: CATALOG_URLS[CatalogCategory.FloorHeating],
      contentPageId: ContentPageId.ProductFloorHeating,
      priceTrigger: CallbackData.FloorHeating,
    },
    {
      id: 'water_heaters',
      icon: '💧',
      title_uz: 'Suv isitgichlar',
      title_ru: 'Водонагреватели',
      isVisible: true,
      sortOrder: 40,
      websiteUrl: '',
      catalogUrl: CATALOG_URLS[CatalogCategory.WaterHeaters],
      contentPageId: ContentPageId.ProductWaterHeaters,
      priceTrigger: CallbackData.WaterHeaters,
    },
    {
      id: 'pumps',
      icon: '⚙️',
      title_uz: 'Nasoslar',
      title_ru: 'Насосы',
      isVisible: true,
      sortOrder: 50,
      websiteUrl: '',
      catalogUrl: CATALOG_URLS[CatalogCategory.Pumps],
      contentPageId: ContentPageId.ProductPumps,
      priceTrigger: CallbackData.Pumps,
    },
  ],
};
