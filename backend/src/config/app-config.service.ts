import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import {
  AppConfig,
  Configuration,
  DatabaseConfig,
  JwtConfig,
  LoggerConfig,
  RateLimitConfig,
  RedisConfig,
  TelegramConfig,
} from './configuration';

/**
 * Typed facade over `@nestjs/config`'s {@link ConfigService}.
 *
 * Provides strongly-typed, namespaced getters so feature modules never deal
 * with raw string keys or `undefined`. Because configuration is validated at
 * boot, every getter is guaranteed to return a defined value.
 */
@Injectable()
export class AppConfigService {
  constructor(private readonly configService: ConfigService<{ configuration: Configuration }>) {}

  private get config(): Configuration {
    // `infer: true` guarantees presence because validation runs at startup.
    return this.configService.get('configuration', { infer: true }) as Configuration;
  }

  get app(): AppConfig {
    return this.config.app;
  }

  get logger(): LoggerConfig {
    return this.config.logger;
  }

  get database(): DatabaseConfig {
    return this.config.database;
  }

  get redis(): RedisConfig {
    return this.config.redis;
  }

  get jwt(): JwtConfig {
    return this.config.jwt;
  }

  get telegram(): TelegramConfig {
    return this.config.telegram;
  }

  get rateLimit(): RateLimitConfig {
    return this.config.rateLimit;
  }

  /** Convenience flag widely used across guards / filters. */
  get isProduction(): boolean {
    return this.config.app.isProduction;
  }
}
