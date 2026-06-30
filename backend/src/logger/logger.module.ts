import { Global, Module } from '@nestjs/common';
import { WinstonModule } from 'nest-winston';
import { AppConfigModule } from '../config/config.module';
import { AppConfigService } from '../config/app-config.service';
import { buildWinstonOptions } from './winston.config';

/**
 * Global logging module.
 *
 * Configures Winston (via `nest-winston`) from validated configuration and
 * exports it so it can be used both as the Nest application logger and injected
 * anywhere through the `WINSTON_MODULE_NEST_PROVIDER` token.
 */
@Global()
@Module({
  imports: [
    WinstonModule.forRootAsync({
      imports: [AppConfigModule],
      inject: [AppConfigService],
      useFactory: (configService: AppConfigService) => buildWinstonOptions(configService.logger),
    }),
  ],
  exports: [WinstonModule],
})
export class AppLoggerModule {}
