/**
 * Callback payloads for content-page navigation. Namespaced under `content:`
 * so they never collide with menu or flow callbacks.
 */
export const ContentAction = {
  /** `content:page:<id>` opens a content page. */
  PagePrefix: 'content:page:',
  /** `content:phone:<value>` reveals a callable phone number. */
  PhonePrefix: 'content:phone:',
} as const;

/** Ids of the content pages shipped today. */
export const ContentPageId = {
  About: 'about',
  Contacts: 'contacts',
  Branches: 'branches',
  Warranty: 'warranty',
  Products: 'products',
  ProductBoilers: 'product_boilers',
  ProductRadiators: 'product_radiators',
  ProductFloorHeating: 'product_floor_heating',
  ProductWaterHeaters: 'product_water_heaters',
  ProductPumps: 'product_pumps',
} as const;

export type ContentPageIdValue = (typeof ContentPageId)[keyof typeof ContentPageId];

/** Build the callback payload that opens a given content page. */
export function contentPageCallback(pageId: string): string {
  return `${ContentAction.PagePrefix}${pageId}`;
}
