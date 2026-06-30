import { Global, Module } from '@nestjs/common';
import { ConfigModule as NestConfigModule } from '@nestjs/config';
import { AppConfigService } from './app-config.service';
import { configurationFactory } from './configuration';
import { validateEnv } from './env.validation';

/**
 * Global configuration module.
 *
 * - Loads `.env` files via `@nestjs/config`.
 * - Validates the environment with Zod (`validateEnv`); boot aborts on failure.
 * - Exposes a typed {@link AppConfigService} application-wide.
 */
@Global()
@Module({
  imports: [
    NestConfigModule.forRoot({
      isGlobal: true,
      cache: true,
      validate: validateEnv,
      load: [() => ({ configuration: configurationFactory() })],
      envFilePath: ['.env', '.env.local'],
    }),
  ],
  providers: [AppConfigService],
  exports: [AppConfigService],
})
export class AppConfigModule {}
