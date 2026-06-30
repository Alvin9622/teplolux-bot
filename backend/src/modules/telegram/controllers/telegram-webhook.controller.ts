import {
  Body,
  Controller,
  HttpCode,
  HttpStatus,
  Inject,
  LoggerService,
  Post,
  UseGuards,
  UsePipes,
} from '@nestjs/common';
import { ApiExcludeController } from '@nestjs/swagger';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { LogEvent } from '../../../logger/log-events';
import { TelegramWebhookGuard } from '../../../common/guards/telegram-webhook.guard';
import { ZodValidationPipe } from '../../../common/pipes/zod-validation.pipe';
import { TelegramUpdateDto, telegramUpdateSchema } from '../dto/telegram-update.dto';
import { TelegramUpdateService } from '../services/telegram-update.service';

/**
 * Inbound Telegram webhook endpoint: `POST /webhook/telegram`.
 *
 * Webhook-only by design (no polling). The request is authenticated by
 * {@link TelegramWebhookGuard} (secret-token header) and validated by Zod.
 *
 * Telegram retries deliveries that are not answered quickly, so the controller
 * acknowledges with `200 OK` immediately and processes the update afterwards;
 * processing errors are logged, never surfaced to Telegram.
 */
@ApiExcludeController()
@Controller('webhook')
@UseGuards(TelegramWebhookGuard)
export class TelegramWebhookController {
  constructor(
    private readonly updateService: TelegramUpdateService,
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
  ) {}

  @Post('telegram')
  @HttpCode(HttpStatus.OK)
  @UsePipes(new ZodValidationPipe(telegramUpdateSchema))
  acknowledge(@Body() update: TelegramUpdateDto): { ok: true } {
    this.logger.log(
      `${LogEvent.WebhookReceived}: update_id=${update.update_id}`,
      TelegramWebhookController.name,
    );

    // Fire-and-forget: never block Telegram's delivery on our processing.
    void this.updateService.process(update).catch((error: unknown) => {
      this.logger.error(
        `${LogEvent.WebhookFailed}: update_id=${update.update_id}`,
        error instanceof Error ? error.stack : String(error),
        TelegramWebhookController.name,
      );
    });

    return { ok: true };
  }
}
