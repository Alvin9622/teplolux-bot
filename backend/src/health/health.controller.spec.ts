import { Test, TestingModule } from '@nestjs/testing';
import { HealthCheckService } from '@nestjs/terminus';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { HealthController } from './health.controller';
import { PrismaHealthIndicator } from './indicators/prisma.health-indicator';
import { RedisHealthIndicator } from './indicators/redis.health-indicator';

describe('HealthController', () => {
  let controller: HealthController;
  let healthService: { check: jest.Mock };

  beforeEach(async () => {
    healthService = {
      check: jest.fn().mockImplementation(async (indicators: Array<() => unknown>) => {
        await Promise.all(indicators.map((indicator) => indicator()));
        return { status: 'ok' };
      }),
    };

    const moduleRef: TestingModule = await Test.createTestingModule({
      controllers: [HealthController],
      providers: [
        { provide: HealthCheckService, useValue: healthService },
        {
          provide: PrismaHealthIndicator,
          useValue: { check: jest.fn().mockResolvedValue({ database: { status: 'up' } }) },
        },
        {
          provide: RedisHealthIndicator,
          useValue: { check: jest.fn().mockResolvedValue({ redis: { status: 'up' } }) },
        },
        { provide: WINSTON_MODULE_NEST_PROVIDER, useValue: { debug: jest.fn() } },
      ],
    }).compile();

    controller = moduleRef.get(HealthController);
  });

  it('aggregates database, redis and application indicators', async () => {
    const result = await controller.check();
    expect(result).toEqual({ status: 'ok' });
    expect(healthService.check).toHaveBeenCalledTimes(1);
    // Three indicators: database, redis, application.
    expect(healthService.check.mock.calls[0][0]).toHaveLength(3);
  });
});
