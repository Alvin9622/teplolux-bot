/**
 * Inline-keyboard callback payloads.
 *
 * Telegram limits `callback_data` to 64 bytes, so values are kept short and
 * centralised here to avoid magic strings and accidental collisions.
 */
export const CallbackData = {
  Boilers: 'cat:boilers',
  Radiators: 'cat:radiators',
  FloorHeating: 'cat:floor_heating',
  Service: 'menu:service',
  Dealer: 'menu:dealer',
  Operator: 'menu:operator',
  Contact: 'menu:contact',
  Location: 'menu:location',
  BackToMenu: 'nav:menu',
  ChangeLanguage: 'menu:lang',
  SelectLangUz: 'lang:uz',
  SelectLangRu: 'lang:ru',
} as const;

export type CallbackDataValue = (typeof CallbackData)[keyof typeof CallbackData];
