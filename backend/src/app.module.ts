import { Module } from '@nestjs/common';
import { APP_FILTER, APP_GUARD, APP_INTERCEPTOR } from '@nestjs/core';
import { ThrottlerGuard, ThrottlerModule } from '@nestjs/throttler';
import { AppConfigModule } from './config/config.module';
import { AppConfigService } from './config/app-config.service';
import { AppLoggerModule } from './logger/logger.module';
import { PrismaModule } from './database/prisma.module';
import { RedisModule } from './redis/redis.module';
import { HealthModule } from './health/health.module';
import { AllExceptionsFilter } from './common/filters/all-exceptions.filter';
import { LoggingInterceptor } from './common/interceptors/logging.interceptor';
import { TelegramModule } from './modules/telegram/telegram.module';
import { AmoCrmModule } from './modules/amocrm/amocrm.module';
import { UsersModule } from './modules/users/users.module';
import { ChatModule } from './modules/chat/chat.module';
import { AuthModule } from './modules/auth/auth.module';

/**
 * Application composition root.
 *
 * Wires the global infrastructure modules (config, logging, database, cache,
 * rate limiting), the active feature modules and the architecture placeholders
 * for future channels/integrations. Cross-cutting concerns (exception filter,
 * logging interceptor, throttler guard) are registered globally here.
 */
@Module({
  imports: [
    // Infrastructure
    AppConfigModule,
    AppLoggerModule,
    PrismaModule,
    RedisModule,
    ThrottlerModule.forRootAsync({
      inject: [AppConfigService],
      useFactory: (config: AppConfigService) => ({
        throttlers: [
          {
            ttl: config.rateLimit.ttlMs,
            limit: config.rateLimit.max,
          },
        ],
      }),
    }),

    // Operational
    HealthModule,

    // Active channels / features
    TelegramModule,

    // Future architecture placeholders (no behaviour wired yet)
    AmoCrmModule,
    UsersModule,
    ChatModule,
    AuthModule,
  ],
  providers: [
    { provide: APP_FILTER, useClass: AllExceptionsFilter },
    { provide: APP_INTERCEPTOR, useClass: LoggingInterceptor },
    { provide: APP_GUARD, useClass: ThrottlerGuard },
  ],
})
export class AppModule {}
