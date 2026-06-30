import { Inject, Injectable, OnModuleDestroy, OnModuleInit } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { LoggerService } from '@nestjs/common';
import { AppConfigService } from '../config/app-config.service';
import { LogEvent } from '../logger/log-events';

/**
 * Prisma client wrapped as an injectable NestJS provider.
 *
 * Manages the database connection lifecycle in step with the application
 * lifecycle and centralises connection logging.
 */
@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit, OnModuleDestroy {
  constructor(
    configService: AppConfigService,
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
  ) {
    super({
      datasources: { db: { url: configService.database.url } },
      log: [
        { level: 'warn', emit: 'event' },
        { level: 'error', emit: 'event' },
      ],
    });
  }

  async onModuleInit(): Promise<void> {
    try {
      await this.$connect();
      this.logger.log('Database connection established', PrismaService.name);
    } catch (error) {
      this.logger.error(
        LogEvent.DatabaseError,
        error instanceof Error ? error.stack : String(error),
        PrismaService.name,
      );
      throw error;
    }
  }

  async onModuleDestroy(): Promise<void> {
    await this.$disconnect();
    this.logger.log('Database connection closed', PrismaService.name);
  }

  /**
   * Lightweight liveness probe used by the health module. Returns `true` when
   * the database answers a trivial query.
   */
  async isHealthy(): Promise<boolean> {
    await this.$queryRaw`SELECT 1`;
    return true;
  }
}
