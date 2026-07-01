import { CompanyContacts } from '../constants/company.constants';
import { CATALOG_URLS, CatalogCategory } from '../content/catalog.config';
import { CompanyConfigService } from './company-config.service';
import { CompanyConfigSource, StaticCompanyConfigSource } from './company-config.source';
import { CompanyConfig } from './company-config.types';

describe('CompanyConfigService (static source)', () => {
  const service = new CompanyConfigService(new StaticCompanyConfigSource());

  it('exposes the structured configuration sections', () => {
    expect(service.company.name).toBeTruthy();
    expect(service.contacts.email).toContain('@');
    expect(service.workingHours).toBeTruthy();
    expect(service.social.telegram).toMatch(/^https?:\/\//);
    expect(service.social.instagram).toMatch(/^https?:\/\//);
    expect(service.social.facebook).toMatch(/^https?:\/\//);
    expect(service.social.youtube).toMatch(/^https?:\/\//);
  });

  it('reuses the existing constants (no duplicated configuration)', () => {
    // Phone/website come from CompanyContacts; catalog from CATALOG_URLS.
    expect(service.contacts.phone).toBe(CompanyContacts.phone);
    expect(service.contacts.website).toBe(CompanyContacts.website);
    expect(service.catalog).toBe(CATALOG_URLS);
    expect(service.catalog[CatalogCategory.Boilers]).toBe(CATALOG_URLS.boilers);
  });
});

describe('CompanyConfigService (swappable source)', () => {
  it('reads whatever source is bound (future DB/CMS ready)', () => {
    const custom: CompanyConfig = {
      company: { name: 'Custom Co' },
      contacts: {
        phone: '+100',
        email: 'a@b.co',
        website: 'https://b.co',
        address: 'Somewhere',
      },
      social: {
        telegram: 'https://t.me/x',
        instagram: 'https://instagram.com/x',
        facebook: 'https://facebook.com/x',
        youtube: 'https://youtube.com/@x',
      },
      workingHours: '24/7',
      catalog: CATALOG_URLS,
    };
    const source: CompanyConfigSource = { load: () => custom };

    const service = new CompanyConfigService(source);

    expect(service.company.name).toBe('Custom Co');
    expect(service.workingHours).toBe('24/7');
    expect(service.config).toBe(custom);
  });
});
