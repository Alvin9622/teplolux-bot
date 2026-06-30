import { CanActivate, ExecutionContext, Inject, Injectable, LoggerService } from '@nestjs/common';
import { timingSafeEqual } from 'node:crypto';
import { Request } from 'express';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { AppConfigService } from '../../config/app-config.service';
import { LogEvent } from '../../logger/log-events';
import { WebhookUnauthorizedException } from '../exceptions';

/** Header Telegram includes on every webhook call when a secret token is set. */
const TELEGRAM_SECRET_HEADER = 'x-telegram-bot-api-secret-token';

/**
 * Authenticates inbound Telegram webhook requests by comparing the
 * `X-Telegram-Bot-Api-Secret-Token` header against the configured secret using
 * a constant-time comparison to avoid timing attacks.
 */
@Injectable()
export class TelegramWebhookGuard implements CanActivate {
  constructor(
    private readonly configService: AppConfigService,
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
  ) {}

  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest<Request>();
    const provided = request.header(TELEGRAM_SECRET_HEADER);
    const expected = this.configService.telegram.webhookSecret;

    if (!provided || !this.isEqual(provided, expected)) {
      this.logger.warn(LogEvent.WebhookFailed, TelegramWebhookGuard.name);
      throw new WebhookUnauthorizedException('Invalid Telegram webhook secret token');
    }

    return true;
  }

  /** Constant-time string comparison resistant to timing analysis. */
  private isEqual(a: string, b: string): boolean {
    const bufferA = Buffer.from(a);
    const bufferB = Buffer.from(b);
    if (bufferA.length !== bufferB.length) {
      return false;
    }
    return timingSafeEqual(bufferA, bufferB);
  }
}
