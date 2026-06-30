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
} as const satisfies Record<string, TranslationKey>;
