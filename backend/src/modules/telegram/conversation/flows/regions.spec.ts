import { UZBEKISTAN_REGION_CHOICES, cityStep } from './regions';
import { I18nService } from '../../../../i18n/i18n.service';
import { Locale } from '../../../../i18n/i18n.types';

describe('Uzbekistan region picker', () => {
  it('offers all 14 first-level regions with unique values', () => {
    expect(UZBEKISTAN_REGION_CHOICES).toHaveLength(14);
    const values = UZBEKISTAN_REGION_CHOICES.map((c) => c.value);
    expect(new Set(values).size).toBe(14);
  });

  it('exposes city as a two-column choice step', () => {
    expect(cityStep.id).toBe('city');
    expect(cityStep.type).toBe('choice');
    expect(cityStep.columns).toBe(2);
    expect(cityStep.choices).toBe(UZBEKISTAN_REGION_CHOICES);
  });

  it('keeps every value within Telegram callback-data limits', () => {
    for (const { value } of UZBEKISTAN_REGION_CHOICES) {
      expect(Buffer.byteLength(`flow:choice:${value}`, 'utf8')).toBeLessThanOrEqual(64);
    }
  });

  it('has a localized label for every region in uz and ru', () => {
    const i18n = new I18nService({ warn: jest.fn() } as never);
    for (const locale of ['uz', 'ru'] as Locale[]) {
      for (const { labelKey } of UZBEKISTAN_REGION_CHOICES) {
        const label = i18n.t(locale, labelKey);
        expect(label).toBeTruthy();
        expect(label).not.toBe(labelKey); // key was actually resolved
      }
    }
  });
});
