import { HttpStatus } from '@nestjs/common';
import { DomainException } from './domain.exception';

export { DomainException } from './domain.exception';

/** Error codes are centralised so they stay consistent and greppable. */
export const ErrorCode = {
  ValidationFailed: 'VALIDATION_FAILED',
  EntityNotFound: 'ENTITY_NOT_FOUND',
  WebhookUnauthorized: 'WEBHOOK_UNAUTHORIZED',
  TelegramApiError: 'TELEGRAM_API_ERROR',
  IntegrationError: 'INTEGRATION_ERROR',
  InternalError: 'INTERNAL_ERROR',
} as const;

/** Raised when incoming data fails validation (Zod / DTO). */
export class ValidationException extends DomainException {
  constructor(
    message = 'Validation failed',
    public readonly details?: unknown,
  ) {
    super(message, HttpStatus.BAD_REQUEST, ErrorCode.ValidationFailed);
  }
}

/** Raised when a requested domain entity does not exist. */
export class EntityNotFoundException extends DomainException {
  constructor(entity: string, identifier?: string | number | bigint) {
    const suffix = identifier !== undefined ? ` (${String(identifier)})` : '';
    super(`${entity} not found${suffix}`, HttpStatus.NOT_FOUND, ErrorCode.EntityNotFound);
  }
}

/** Raised when a webhook request cannot be authenticated. */
export class WebhookUnauthorizedException extends DomainException {
  constructor(message = 'Webhook request is not authorized') {
    super(message, HttpStatus.UNAUTHORIZED, ErrorCode.WebhookUnauthorized);
  }
}

/** Raised when the Telegram Bot API returns an error. */
export class TelegramApiException extends DomainException {
  constructor(message = 'Telegram API request failed') {
    super(message, HttpStatus.BAD_GATEWAY, ErrorCode.TelegramApiError);
  }
}

/** Raised when an external CRM / integration call fails. */
export class IntegrationException extends DomainException {
  constructor(message = 'External integration request failed') {
    super(message, HttpStatus.BAD_GATEWAY, ErrorCode.IntegrationError);
  }
}
