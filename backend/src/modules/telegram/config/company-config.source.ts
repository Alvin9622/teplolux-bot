import { Injectable } from '@nestjs/common';
import { CompanyContacts } from '../constants/company.constants';
import { CATALOG_URLS } from '../content/catalog.config';
import { CompanyConfig } from './company-config.types';

/** DI token for the swappable {@link CompanyConfigSource}. */
export const COMPANY_CONFIG_SOURCE = Symbol('COMPANY_CONFIG_SOURCE');

/**
 * A source of company configuration.
 *
 * `load()` is synchronous so consumers (Telegram handlers) never need to await
 * it. A future database / admin-panel / CMS source can fetch asynchronously on
 * startup and cache a snapshot, still returning it synchronously here — so the
 * binding of {@link COMPANY_CONFIG_SOURCE} can be swapped with zero handler
 * changes.
 */
export interface CompanyConfigSource {
  load(): CompanyConfig;
}

/**
 * Default, code-based configuration source.
 *
 * Composes the existing constants (`CompanyContacts`, `CATALOG_URLS`) with the
 * remaining company facts so there is a single source of truth and no
 * duplicated configuration. Replace the {@link COMPANY_CONFIG_SOURCE} binding
 * with a persistent source later without touching the handlers.
 */
@Injectable()
export class StaticCompanyConfigSource implements CompanyConfigSource {
  private readonly config: CompanyConfig = {
    company: { name: 'Teplolux' },
    contacts: {
      phone: CompanyContacts.phone,
      email: 'info@teplolux.example.com',
      website: CompanyContacts.website,
      address: 'Toshkent, Chilonzor 1',
    },
    social: {
      telegram: 'https://t.me/teplolux',
      instagram: 'https://instagram.com/teplolux',
      facebook: 'https://facebook.com/teplolux',
      youtube: 'https://youtube.com/@teplolux',
    },
    workingHours: 'Mon–Sat: 09:00–18:00',
    catalog: CATALOG_URLS,
  };

  load(): CompanyConfig {
    return this.config;
  }
}
