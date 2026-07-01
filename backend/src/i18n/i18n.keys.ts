import { TranslationKey } from './i18n.types';

/**
 * Centralised translation-key constants.
 *
 * Referencing `TKey.welcome` instead of the raw `'welcome'` string keeps call
 * sites free of magic strings and—thanks to the `satisfies` clause—guarantees
 * at compile time that every key actually exists in the locale catalogs.
 */
export const TKey = {
  languagePrompt: 'language.prompt',
  languageChanged: 'language.changed',

  welcome: 'welcome',
  help: 'help',
  catalogIntro: 'catalog.intro',

  categoryBoilers: 'category.boilers',
  categoryRadiators: 'category.radiators',
  categoryFloorHeating: 'category.floorHeating',

  service: 'service',
  dealer: 'dealer',
  operator: 'operator',
  contact: 'contact',
  locationIntro: 'location.intro',
  locationDetail: 'location.detail',

  unknownCommand: 'unknownCommand',
  fallback: 'fallback',
  callbackAcknowledged: 'callbackAcknowledged',

  menuBoilers: 'menu.boilers',
  menuRadiators: 'menu.radiators',
  menuFloorHeating: 'menu.floorHeating',
  menuService: 'menu.service',
  menuDealer: 'menu.dealer',
  menuOperator: 'menu.operator',
  menuContact: 'menu.contact',
  menuLocation: 'menu.location',
  menuChangeLanguage: 'menu.changeLanguage',
  menuBack: 'menu.back',
  menuAbout: 'menu.about',

  contentButtonContacts: 'content.button.contacts',
  contentButtonBranches: 'content.button.branches',
  contentButtonWarranty: 'content.button.warranty',
  contentButtonWebsite: 'content.button.website',
  contentButtonCall: 'content.button.call',
  contentButtonBack: 'content.button.back',
  contentButtonMainMenu: 'content.button.mainMenu',
  contentCallMessage: 'content.callMessage',
  contentAboutTitle: 'content.about.title',
  contentAboutDescription: 'content.about.description',
  contentContactsTitle: 'content.contacts.title',
  contentContactsDescription: 'content.contacts.description',
  contentBranchesTitle: 'content.branches.title',
  contentBranchesDescription: 'content.branches.description',
  contentWarrantyTitle: 'content.warranty.title',
  contentWarrantyDescription: 'content.warranty.description',

  flowStarted: 'flow.started',
  flowTopicProduct: 'flow.topic.product',
  flowTopicService: 'flow.topic.service',
  flowTopicDealer: 'flow.topic.dealer',
  flowTopicOperator: 'flow.topic.operator',
  flowPromptFullName: 'flow.prompt.fullName',
  flowPromptPhone: 'flow.prompt.phone',
  flowPromptCity: 'flow.prompt.city',
  flowPromptComment: 'flow.prompt.comment',
  flowErrorFullName: 'flow.error.fullName',
  flowErrorPhone: 'flow.error.phone',
  flowErrorCity: 'flow.error.city',
  flowButtonShareContact: 'flow.button.shareContact',
  flowButtonShareLocation: 'flow.button.shareLocation',
  flowButtonCancel: 'flow.button.cancel',
  flowButtonBack: 'flow.button.back',
  flowButtonSkip: 'flow.button.skip',
  flowButtonSubmit: 'flow.button.submit',
  flowButtonEdit: 'flow.button.edit',
  flowSummaryTitle: 'flow.summary.title',
  flowSummaryTopic: 'flow.summary.topic',
  flowSummaryFullName: 'flow.summary.fullName',
  flowSummaryPhone: 'flow.summary.phone',
  flowSummaryCity: 'flow.summary.city',
  flowSummaryComment: 'flow.summary.comment',
  flowSummaryEmpty: 'flow.summary.empty',
  flowEditChoose: 'flow.editChoose',
  flowCancelled: 'flow.cancelled',
  flowSubmitted: 'flow.submitted',
} as const satisfies Record<string, TranslationKey>;
