import { Module } from '@nestjs/common';
import { CompanyConfigService } from './company-config.service';
import { COMPANY_CONFIG_SOURCE, StaticCompanyConfigSource } from './company-config.source';

/**
 * Company configuration module.
 *
 * Binds the default static source to {@link COMPANY_CONFIG_SOURCE} and exports
 * {@link CompanyConfigService}. To move configuration to a database / admin
 * panel / CMS later, replace only the `useClass` binding here — no changes to
 * the Telegram handlers that consume the service.
 */
@Module({
  providers: [
    { provide: COMPANY_CONFIG_SOURCE, useClass: StaticCompanyConfigSource },
    CompanyConfigService,
  ],
  exports: [CompanyConfigService],
})
export class CompanyConfigModule {}
