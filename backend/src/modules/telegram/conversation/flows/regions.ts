import { TKey } from '../../../../i18n/i18n.keys';
import { ChoiceOption, FlowStep } from '../conversation.types';

/**
 * The administrative regions of Uzbekistan (12 provinces + Tashkent city + the
 * Republic of Karakalpakstan), offered as a ready-made picker so the customer
 * selects their region instead of typing a free-text city.
 *
 * The `value` is the canonical Uzbek name — it is what gets stored and shown to
 * operators — while `labelKey` resolves the localised button/summary label. All
 * values stay well under Telegram's 64-byte callback-data limit.
 */
export const UZBEKISTAN_REGION_CHOICES: ReadonlyArray<ChoiceOption> = [
  { value: 'Toshkent shahri', labelKey: TKey.regionTashkentCity },
  { value: 'Toshkent viloyati', labelKey: TKey.regionTashkentRegion },
  { value: 'Andijon viloyati', labelKey: TKey.regionAndijan },
  { value: 'Buxoro viloyati', labelKey: TKey.regionBukhara },
  { value: "Farg'ona viloyati", labelKey: TKey.regionFergana },
  { value: 'Jizzax viloyati', labelKey: TKey.regionJizzakh },
  { value: 'Namangan viloyati', labelKey: TKey.regionNamangan },
  { value: 'Navoiy viloyati', labelKey: TKey.regionNavoi },
  { value: 'Qashqadaryo viloyati', labelKey: TKey.regionKashkadarya },
  { value: 'Samarqand viloyati', labelKey: TKey.regionSamarkand },
  { value: 'Sirdaryo viloyati', labelKey: TKey.regionSyrdarya },
  { value: 'Surxondaryo viloyati', labelKey: TKey.regionSurkhandarya },
  { value: 'Xorazm viloyati', labelKey: TKey.regionKhorezm },
  { value: "Qoraqalpog'iston Respublikasi", labelKey: TKey.regionKarakalpakstan },
];

/**
 * Shared "which region are you from?" step. A two-column choice picker reused by
 * every flow that used to collect a free-text city, so the question looks and
 * behaves the same everywhere. Choice steps are answered via the inline buttons;
 * the pass-through `validate` only trims (the engine already restricts input to
 * the declared options).
 */
export const cityStep: FlowStep = {
  id: 'city',
  promptKey: TKey.flowPromptCity,
  summaryLabelKey: TKey.flowSummaryCity,
  type: 'choice',
  choices: UZBEKISTAN_REGION_CHOICES,
  columns: 2,
  validate: (raw) => ({ ok: true, value: raw.trim() }),
};
