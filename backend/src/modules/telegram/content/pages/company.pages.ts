import { TKey } from '../../../../i18n/i18n.keys';
import { CallbackData } from '../../constants/callback-data.constants';
import { CompanyContacts } from '../../constants/company.constants';
import { ContentPageId } from '../content.constants';
import { ContentPage } from '../content.types';

/** Reusable button builders shared by the pages. */
const websiteButton = {
  labelKey: TKey.contentButtonWebsite,
  action: { type: 'url', url: CompanyContacts.website },
} as const;

const callButton = {
  labelKey: TKey.contentButtonCall,
  action: { type: 'phone', phone: CompanyContacts.phone },
} as const;

const backButton = { labelKey: TKey.contentButtonBack, action: { type: 'back' } } as const;
const mainMenuButton = {
  labelKey: TKey.contentButtonMainMenu,
  action: { type: 'mainMenu' },
} as const;

/** About Teplolux — the root informational page (linked from the main menu). */
const about: ContentPage = {
  id: ContentPageId.About,
  titleKey: TKey.contentAboutTitle,
  descriptionKey: TKey.contentAboutDescription,
  buttons: [
    [
      {
        labelKey: TKey.contentButtonContacts,
        action: { type: 'page', pageId: ContentPageId.Contacts },
      },
      {
        labelKey: TKey.contentButtonBranches,
        action: { type: 'page', pageId: ContentPageId.Branches },
      },
    ],
    [
      {
        labelKey: TKey.contentButtonWarranty,
        action: { type: 'page', pageId: ContentPageId.Warranty },
      },
    ],
    [websiteButton, callButton],
    [mainMenuButton],
  ],
};

const contacts: ContentPage = {
  id: ContentPageId.Contacts,
  titleKey: TKey.contentContactsTitle,
  descriptionKey: TKey.contentContactsDescription,
  parentId: ContentPageId.About,
  buttons: [
    [callButton, websiteButton],
    [backButton, mainMenuButton],
  ],
};

const branches: ContentPage = {
  id: ContentPageId.Branches,
  titleKey: TKey.contentBranchesTitle,
  descriptionKey: TKey.contentBranchesDescription,
  parentId: ContentPageId.About,
  buttons: [[backButton, mainMenuButton]],
};

const warranty: ContentPage = {
  id: ContentPageId.Warranty,
  titleKey: TKey.contentWarrantyTitle,
  descriptionKey: TKey.contentWarrantyDescription,
  parentId: ContentPageId.About,
  buttons: [
    // Demonstrates a "start conversation flow" button (reuses the service trigger).
    [{ labelKey: TKey.menuService, action: { type: 'flow', trigger: CallbackData.Service } }],
    [
      {
        labelKey: TKey.contentButtonContacts,
        action: { type: 'page', pageId: ContentPageId.Contacts },
      },
    ],
    [backButton, mainMenuButton],
  ],
};

/** All content pages shipped today. */
export const companyPages: ReadonlyArray<ContentPage> = [about, contacts, branches, warranty];
