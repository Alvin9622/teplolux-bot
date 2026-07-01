import { TKey } from '../../../../i18n/i18n.keys';
import { TranslationKey } from '../../../../i18n/i18n.types';
import { CallbackData } from '../../constants/callback-data.constants';
import { CompanyContacts } from '../../constants/company.constants';
import { CompanyConfig } from '../../config/company-config.types';
import { CATALOG_URLS, CatalogCategory } from '../catalog.config';
import { ContentPageId } from '../content.constants';
import { ContentButton, ContentPage } from '../content.types';

/** Reusable button builders shared by the pages. */
const websiteButton: ContentButton = {
  labelKey: TKey.contentButtonWebsite,
  action: { type: 'url', url: CompanyContacts.website },
};

const backButton: ContentButton = { labelKey: TKey.contentButtonBack, action: { type: 'back' } };

/** Contact Operator starts the existing Contact Request flow (topic OPERATOR). */
const operatorButton: ContentButton = {
  labelKey: TKey.contentButtonOperator,
  action: { type: 'flow', trigger: CallbackData.Operator },
};

// ---------------------------------------------------------------------------
// About / Contacts (informational — never start the lead flow themselves)
// ---------------------------------------------------------------------------

const about: ContentPage = {
  id: ContentPageId.About,
  titleKey: TKey.contentAboutTitle,
  descriptionKey: TKey.contentAboutDescription,
  buttons: [
    [websiteButton],
    [
      {
        labelKey: TKey.contentButtonContacts,
        action: { type: 'page', pageId: ContentPageId.Contacts },
      },
    ],
    [backButton],
  ],
};

const contacts: ContentPage = {
  id: ContentPageId.Contacts,
  titleKey: TKey.contentContactsTitle,
  descriptionKey: TKey.contentContactsDescription,
  // All contact/company values are read from configuration, not hardcoded copy.
  descriptionParams: (c: CompanyConfig) => ({
    companyName: c.company.name,
    phone: c.contacts.phone,
    email: c.contacts.email,
    website: c.contacts.website,
    address: c.contacts.address,
    workingHours: c.workingHours,
    telegram: c.social.telegram,
    instagram: c.social.instagram,
    facebook: c.social.facebook,
    youtube: c.social.youtube,
  }),
  buttons: [
    // Location reuses the existing menu callback handler (sends the map pin).
    [
      {
        labelKey: TKey.contentButtonLocation,
        action: { type: 'callback', data: CallbackData.Location },
      },
    ],
    [operatorButton],
    [backButton],
  ],
};

// ---------------------------------------------------------------------------
// Products — a catalog of informational category pages (no lead flow here)
// ---------------------------------------------------------------------------

/** Build a product category page. "Request Price" starts the lead flow. */
function productPage(
  id: string,
  titleKey: TranslationKey,
  descriptionKey: TranslationKey,
  priceTrigger: string,
  viewCatalogUrl: string,
): ContentPage {
  return {
    id,
    titleKey,
    descriptionKey,
    parentId: ContentPageId.Products,
    buttons: [
      [
        {
          labelKey: TKey.contentButtonViewCatalog,
          action: { type: 'url', url: viewCatalogUrl },
        },
      ],
      // Request Price is the ONLY product entry point into the Contact Request flow.
      [
        {
          labelKey: TKey.contentButtonRequestPrice,
          action: { type: 'flow', trigger: priceTrigger },
        },
      ],
      [operatorButton],
      [backButton],
    ],
  };
}

const productBoilers = productPage(
  ContentPageId.ProductBoilers,
  TKey.contentProductBoilersTitle,
  TKey.contentProductBoilersDescription,
  CallbackData.Boilers,
  CATALOG_URLS[CatalogCategory.Boilers],
);
const productRadiators = productPage(
  ContentPageId.ProductRadiators,
  TKey.contentProductRadiatorsTitle,
  TKey.contentProductRadiatorsDescription,
  CallbackData.Radiators,
  CATALOG_URLS[CatalogCategory.Radiators],
);
const productFloorHeating = productPage(
  ContentPageId.ProductFloorHeating,
  TKey.contentProductFloorHeatingTitle,
  TKey.contentProductFloorHeatingDescription,
  CallbackData.FloorHeating,
  CATALOG_URLS[CatalogCategory.FloorHeating],
);
const productWaterHeaters = productPage(
  ContentPageId.ProductWaterHeaters,
  TKey.contentProductWaterHeatersTitle,
  TKey.contentProductWaterHeatersDescription,
  CallbackData.WaterHeaters,
  CATALOG_URLS[CatalogCategory.WaterHeaters],
);
const productPumps = productPage(
  ContentPageId.ProductPumps,
  TKey.contentProductPumpsTitle,
  TKey.contentProductPumpsDescription,
  CallbackData.Pumps,
  CATALOG_URLS[CatalogCategory.Pumps],
);

/** Products landing page — lists the category pages. */
const products: ContentPage = {
  id: ContentPageId.Products,
  titleKey: TKey.contentProductsTitle,
  descriptionKey: TKey.contentProductsDescription,
  buttons: [
    [
      {
        labelKey: TKey.contentProductBoilersTitle,
        action: { type: 'page', pageId: ContentPageId.ProductBoilers },
      },
    ],
    [
      {
        labelKey: TKey.contentProductRadiatorsTitle,
        action: { type: 'page', pageId: ContentPageId.ProductRadiators },
      },
    ],
    [
      {
        labelKey: TKey.contentProductFloorHeatingTitle,
        action: { type: 'page', pageId: ContentPageId.ProductFloorHeating },
      },
    ],
    [
      {
        labelKey: TKey.contentProductWaterHeatersTitle,
        action: { type: 'page', pageId: ContentPageId.ProductWaterHeaters },
      },
    ],
    [
      {
        labelKey: TKey.contentProductPumpsTitle,
        action: { type: 'page', pageId: ContentPageId.ProductPumps },
      },
    ],
    [backButton],
  ],
};

// ---------------------------------------------------------------------------
// Branches / Warranty — retained from earlier work (still valid content pages).
// ---------------------------------------------------------------------------

const branches: ContentPage = {
  id: ContentPageId.Branches,
  titleKey: TKey.contentBranchesTitle,
  descriptionKey: TKey.contentBranchesDescription,
  parentId: ContentPageId.About,
  buttons: [[backButton]],
};

const warranty: ContentPage = {
  id: ContentPageId.Warranty,
  titleKey: TKey.contentWarrantyTitle,
  descriptionKey: TKey.contentWarrantyDescription,
  parentId: ContentPageId.About,
  buttons: [[operatorButton], [backButton]],
};

/** All content pages shipped today. */
export const companyPages: ReadonlyArray<ContentPage> = [
  about,
  contacts,
  products,
  productBoilers,
  productRadiators,
  productFloorHeating,
  productWaterHeaters,
  productPumps,
  branches,
  warranty,
];
