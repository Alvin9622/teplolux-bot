import { Global, Module } from '@nestjs/common';
import { I18nService } from './i18n.service';

/**
 * Global internationalisation module.
 *
 * Exposes the {@link I18nService} application-wide so any channel/feature can
 * translate user-facing copy without depending on hardcoded strings.
 */
@Global()
@Module({
  providers: [I18nService],
  exports: [I18nService],
})
export class I18nModule {}
