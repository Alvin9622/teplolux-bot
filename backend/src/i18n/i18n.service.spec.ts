import { I18nService } from './i18n.service';
import { TKey } from './i18n.keys';

describe('I18nService', () => {
  let logger: { warn: jest.Mock };
  let i18n: I18nService;

  beforeEach(() => {
    logger = { warn: jest.fn() };
    i18n = new I18nService(logger as never);
  });

  it('translates a key in Uzbek and Russian', () => {
    expect(i18n.t('uz', TKey.menuBoilers)).toBe('🏠 Kotyollar');
    expect(i18n.t('ru', TKey.menuBoilers)).toBe('🏠 Котлы');
  });

  it('interpolates parameters', () => {
    expect(i18n.t('ru', TKey.welcome, { name: 'Иван' })).toContain('Иван');
    expect(i18n.t('uz', TKey.locationDetail, { lat: 41.3, lng: 69.2 })).toContain('41.3,69.2');
  });

  it('resolves nested dotted keys', () => {
    expect(i18n.t('uz', TKey.categoryBoilers)).toContain('Kotyollar');
  });

  it('builds a locale-scoped translator', () => {
    const t = i18n.scoped('ru');
    expect(t(TKey.menuContact)).toBe('📞 Контакты');
  });

  it('reports no catalog mismatch between uz and ru', () => {
    i18n.onModuleInit();
    expect(logger.warn).not.toHaveBeenCalled();
  });
});
