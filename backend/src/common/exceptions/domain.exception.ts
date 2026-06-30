import { HttpException, HttpStatus } from '@nestjs/common';

/**
 * Base class for all application-specific exceptions.
 *
 * Extends Nest's {@link HttpException} so the framework keeps mapping it to an
 * HTTP response, while adding a stable machine-readable `errorCode` used by the
 * global exception filter and API clients. Internal details are never leaked:
 * the public `message` is safe to expose.
 */
export abstract class DomainException extends HttpException {
  /** Stable, machine-readable identifier (e.g. `TELEGRAM_WEBHOOK_UNAUTHORIZED`). */
  public readonly errorCode: string;

  protected constructor(message: string, status: HttpStatus, errorCode: string) {
    super(message, status);
    this.errorCode = errorCode;
  }
}
