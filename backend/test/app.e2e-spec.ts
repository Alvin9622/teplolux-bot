import { applyTestEnv } from './setup-e2e-env';
applyTestEnv();

import { INestApplication, RequestMethod } from '@nestjs/common';
import { Test, TestingModule } from '@nestjs/testing';
import request from 'supertest';
import { AppModule } from '../src/app.module';
import { PrismaService } from '../src/database/prisma.service';
import { RedisService } from '../src/redis/redis.service';
import { TelegramUpdateService } from '../src/modules/telegram/services/telegram-update.service';

/** Fakes that satisfy the lifecycle + health contracts without real infra. */
const prismaFake = {
  onModuleInit: jest.fn(),
  onModuleDestroy: jest.fn(),
  isHealthy: jest.fn().mockResolvedValue(true),
};
const redisFake = {
  onModuleInit: jest.fn(),
  onModuleDestroy: jest.fn(),
  isHealthy: jest.fn().mockResolvedValue(true),
};
const updateServiceFake = { process: jest.fn().mockResolvedValue(undefined) };

describe('Application (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleRef: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    })
      .overrideProvider(PrismaService)
      .useValue(prismaFake)
      .overrideProvider(RedisService)
      .useValue(redisFake)
      .overrideProvider(TelegramUpdateService)
      .useValue(updateServiceFake)
      .compile();

    app = moduleRef.createNestApplication();
    app.setGlobalPrefix('api', {
      exclude: [
        { path: 'health', method: RequestMethod.ALL },
        { path: 'webhook/telegram', method: RequestMethod.POST },
      ],
    });
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('GET /health reports an OK status with all indicators up', async () => {
    const response = await request(app.getHttpServer()).get('/health').expect(200);
    expect(response.body.status).toBe('ok');
    expect(response.body.info).toHaveProperty('database');
    expect(response.body.info).toHaveProperty('redis');
    expect(response.body.info).toHaveProperty('application');
  });

  it('POST /webhook/telegram is rejected without the secret token', async () => {
    await request(app.getHttpServer()).post('/webhook/telegram').send({ update_id: 1 }).expect(401);
  });

  it('POST /webhook/telegram is accepted with the correct secret token', async () => {
    await request(app.getHttpServer())
      .post('/webhook/telegram')
      .set('X-Telegram-Bot-Api-Secret-Token', 'super-secret-webhook-token')
      .send({
        update_id: 1,
        message: {
          message_id: 1,
          date: 1,
          chat: { id: 1, type: 'private' },
          from: { id: 1, is_bot: false, first_name: 'A' },
          text: '/start',
        },
      })
      .expect(200)
      .expect({ ok: true });

    expect(updateServiceFake.process).toHaveBeenCalled();
  });
});
