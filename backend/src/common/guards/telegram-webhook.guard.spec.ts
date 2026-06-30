import { ExecutionContext } from '@nestjs/common';
import { AppConfigService } from '../../config/app-config.service';
import { WebhookUnauthorizedException } from '../exceptions';
import { TelegramWebhookGuard } from './telegram-webhook.guard';

const SECRET = 'correct-webhook-secret';

function contextWithHeader(value?: string): ExecutionContext {
  return {
    switchToHttp: () => ({
      getRequest: () => ({
        header: (name: string) =>
          name.toLowerCase() === 'x-telegram-bot-api-secret-token' ? value : undefined,
      }),
    }),
  } as unknown as ExecutionContext;
}

describe('TelegramWebhookGuard', () => {
  let guard: TelegramWebhookGuard;

  beforeEach(() => {
    const config = { telegram: { webhookSecret: SECRET } } as AppConfigService;
    const logger = { warn: jest.fn() };
    guard = new TelegramWebhookGuard(config, logger as never);
  });

  it('allows requests carrying the correct secret token', () => {
    expect(guard.canActivate(contextWithHeader(SECRET))).toBe(true);
  });

  it('rejects requests with a wrong secret token', () => {
    expect(() => guard.canActivate(contextWithHeader('wrong'))).toThrow(
      WebhookUnauthorizedException,
    );
  });

  it('rejects requests with no secret token header', () => {
    expect(() => guard.canActivate(contextWithHeader(undefined))).toThrow(
      WebhookUnauthorizedException,
    );
  });
});
