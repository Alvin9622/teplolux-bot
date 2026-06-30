import { Controller, Get, Inject, LoggerService } from '@nestjs/common';
import {
  HealthCheck,
  HealthCheckResult,
  HealthCheckService,
  HealthIndicatorResult,
} from '@nestjs/terminus';
import { ApiOkResponse, ApiTags } from '@nestjs/swagger';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { LogEvent } from '../logger/log-events';
import { APP_VERSION } from '../common/constants/app.constants';
import { PrismaHealthIndicator } from './indicators/prisma.health-indicator';
import { RedisHealthIndicator } from './indicators/redis.health-indicator';

/**
 * Liveness / readiness endpoint.
 *
 * `GET /health` reports database status, Redis status, the application version
 * and process uptime, aggregated by Terminus into a standard health envelope.
 */
@ApiTags('Health')
@Controller('health')
export class HealthController {
  constructor(
    private readonly health: HealthCheckService,
    private readonly prismaIndicator: PrismaHealthIndicator,
    private readonly redisIndicator: RedisHealthIndicator,
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
  ) {}

  @Get()
  @HealthCheck()
  @ApiOkResponse({ description: 'Aggregated application health report.' })
  async check(): Promise<HealthCheckResult> {
    this.logger.debug?.(LogEvent.HealthCheck, HealthController.name);
    return this.health.check([
      () => this.prismaIndicator.check('database'),
      () => this.redisIndicator.check('redis'),
      () => this.applicationInfo(),
    ]);
  }

  /** Static application metadata surfaced as a health "indicator". */
  private applicationInfo(): HealthIndicatorResult {
    return {
      application: {
        status: 'up',
        version: APP_VERSION,
        uptimeSeconds: Math.floor(process.uptime()),
      },
    };
  }
}
