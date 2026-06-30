import { Test, TestingModule } from '@nestjs/testing';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { TelegramWebhookGuard } from '../../../common/guards/telegram-webhook.guard';
import { TelegramUpdateService } from '../services/telegram-update.service';
import { TelegramUpdateDto } from '../dto/telegram-update.dto';
import { TelegramWebhookController } from './telegram-webhook.controller';

describe('TelegramWebhookController', () => {
  let controller: TelegramWebhookController;
  let updateService: { process: jest.Mock };

  const update: TelegramUpdateDto = {
    update_id: 555,
    message: {
      message_id: 1,
      date: 1,
      chat: { id: 1, type: 'private' },
      from: { id: 1, is_bot: false, first_name: 'A' },
      text: '/start',
    },
  };

  beforeEach(async () => {
    updateService = { process: jest.fn().mockResolvedValue(undefined) };

    const moduleRef: TestingModule = await Test.createTestingModule({
      controllers: [TelegramWebhookController],
      providers: [
        { provide: TelegramUpdateService, useValue: updateService },
        {
          provide: WINSTON_MODULE_NEST_PROVIDER,
          useValue: { log: jest.fn(), warn: jest.fn(), error: jest.fn() },
        },
      ],
    })
      .overrideGuard(TelegramWebhookGuard)
      .useValue({ canActivate: () => true })
      .compile();

    controller = moduleRef.get(TelegramWebhookController);
  });

  it('acknowledges Telegram immediately with { ok: true }', () => {
    expect(controller.acknowledge(update)).toEqual({ ok: true });
  });

  it('delegates processing to the update service', () => {
    controller.acknowledge(update);
    expect(updateService.process).toHaveBeenCalledWith(update);
  });

  it('does not throw when processing rejects (errors are logged)', async () => {
    updateService.process.mockRejectedValueOnce(new Error('boom'));
    expect(() => controller.acknowledge(update)).not.toThrow();
    // Allow the fire-and-forget rejection handler to run.
    await Promise.resolve();
  });
});
