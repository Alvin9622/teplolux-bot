import { CallbackData } from '../constants/callback-data.constants';
import { contentPageCallback, ContentPageId } from './content.constants';
import {
  childCallback,
  findProductNode,
  parsePnav,
  pnavCallback,
  PRODUCT_NAV_PAGE_SIZE,
  PRODUCT_ROOT_ID,
  PRODUCT_TREE,
  ProductNode,
  productPageCount,
  productPageSlice,
} from './product-tree';

describe('product-tree', () => {
  it('exposes the Products root with the five current categories as leaves', () => {
    expect(PRODUCT_TREE.id).toBe(PRODUCT_ROOT_ID);
    expect((PRODUCT_TREE.children ?? []).map((c) => c.id)).toEqual([
      'boilers',
      'radiators',
      'floor_heating',
      'water_heaters',
      'pumps',
    ]);
  });

  it('finds nodes by id (including nested ones)', () => {
    expect(findProductNode('boilers')?.id).toBe('boilers');
    expect(findProductNode(PRODUCT_ROOT_ID)?.id).toBe(PRODUCT_ROOT_ID);
    expect(findProductNode('nope')).toBeUndefined();
  });

  it('links a leaf-with-content child to the existing content page callback', () => {
    const boilers = findProductNode('boilers') as ProductNode;
    expect(childCallback(boilers)).toBe(contentPageCallback(ContentPageId.ProductBoilers));
    // The leaf reuses the existing Request Price flow trigger.
    expect(boilers.priceTrigger).toBe(CallbackData.Boilers);
  });

  it('links a node-with-children to the next navigation level', () => {
    const parent: ProductNode = {
      id: 'p',
      titleKey: PRODUCT_TREE.titleKey,
      children: [{ id: 'c', titleKey: PRODUCT_TREE.titleKey }],
    };
    expect(childCallback(parent)).toBe(pnavCallback('p'));
  });

  it('round-trips pnav callbacks (with and without a page)', () => {
    expect(pnavCallback('boilers')).toBe('pnav:boilers');
    expect(pnavCallback('boilers', 2)).toBe('pnav:boilers:2');
    expect(parsePnav('pnav:boilers')).toEqual({ nodeId: 'boilers', page: 0 });
    expect(parsePnav('pnav:boilers:2')).toEqual({ nodeId: 'boilers', page: 2 });
    expect(parsePnav('content:page:x')).toBeNull();
  });

  it('paginates large child lists at 6 per page and clamps out-of-range pages', () => {
    const items = Array.from({ length: 14 }, (_, i) => i);
    expect(PRODUCT_NAV_PAGE_SIZE).toBe(6);
    expect(productPageCount(items.length)).toBe(3);

    const first = productPageSlice(items, 0);
    expect(first.items).toEqual([0, 1, 2, 3, 4, 5]);
    expect(first.pages).toBe(3);

    const last = productPageSlice(items, 2);
    expect(last.items).toEqual([12, 13]);

    // Out-of-range requests clamp to the last page.
    expect(productPageSlice(items, 99).page).toBe(2);
    expect(productPageSlice(items, -5).page).toBe(0);
  });
});
