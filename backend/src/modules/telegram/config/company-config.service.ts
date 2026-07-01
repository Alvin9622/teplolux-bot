import { Inject, Injectable } from '@nestjs/common';
import { CatalogCategoryId } from '../content/catalog.config';
import { COMPANY_CONFIG_SOURCE, CompanyConfigSource } from './company-config.source';
import { CompanyConfig, CompanyInfo, ContactInfo, SocialLinks } from './company-config.types';

/**
 * Single access point for company configuration.
 *
 * Reads from the injected {@link CompanyConfigSource} and exposes typed,
 * namespaced getters (company / contacts / social / workingHours / catalog).
 * Consumers depend on this service only, so the underlying source can be
 * swapped for a database / admin panel / CMS with no handler changes.
 */
@Injectable()
export class CompanyConfigService {
  constructor(@Inject(COMPANY_CONFIG_SOURCE) private readonly source: CompanyConfigSource) {}

  /** The full configuration snapshot. */
  get config(): CompanyConfig {
    return this.source.load();
  }

  get company(): CompanyInfo {
    return this.config.company;
  }

  get contacts(): ContactInfo {
    return this.config.contacts;
  }

  get social(): SocialLinks {
    return this.config.social;
  }

  get workingHours(): string {
    return this.config.workingHours;
  }

  get catalog(): Readonly<Record<CatalogCategoryId, string>> {
    return this.config.catalog;
  }
}
