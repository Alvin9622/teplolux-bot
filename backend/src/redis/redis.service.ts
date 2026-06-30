import { Inject, Injectable, LoggerService, OnModuleDestroy, OnModuleInit } from '@nestjs/common';
import Redis from 'ioredis';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { AppConfigService } from '../config/app-config.service';
import { LogEvent } from '../logger/log-events';

/**
 * Thin, lifecycle-aware wrapper around an `ioredis` client.
 *
 * Used today for health checks and as the foundation for future caching,
 * rate-limit stores, FSM/session state and queue backends.
 */
@Injectable()
export class RedisService implements OnModuleInit, OnModuleDestroy {
  private readonly client: Redis;

  constructor(
    configService: AppConfigService,
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
  ) {
    const { host, port, password, db } = configService.redis;
    this.client = new Redis({
      host,
      port,
      db,
      password: password.length > 0 ? password : undefined,
      lazyConnect: true,
      maxRetriesPerRequest: 3,
      enableReadyCheck: true,
    });

    this.client.on('error', (error: Error) => {
      this.logger.error(LogEvent.RedisError, error.stack, RedisService.name);
    });
  }

  async onModuleInit(): Promise<void> {
    await this.client.connect();
    this.logger.log('Redis connection established', RedisService.name);
  }

  async onModuleDestroy(): Promise<void> {
    await this.client.quit();
    this.logger.log('Redis connection closed', RedisService.name);
  }

  /** Direct access to the underlying client for advanced operations. */
  get instance(): Redis {
    return this.client;
  }

  /** Liveness probe used by the health module. */
  async isHealthy(): Promise<boolean> {
    const pong = await this.client.ping();
    return pong === 'PONG';
  }
}
