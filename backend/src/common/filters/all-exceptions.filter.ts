import {
  ArgumentsHost,
  Catch,
  ExceptionFilter,
  HttpException,
  HttpStatus,
  Inject,
  LoggerService,
} from '@nestjs/common';
import { Request, Response } from 'express';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { AppConfigService } from '../../config/app-config.service';
import { DomainException, ErrorCode } from '../exceptions';

/** Shape of every error response returned by the API. */
interface ErrorResponseBody {
  readonly statusCode: number;
  readonly errorCode: string;
  readonly message: string;
  readonly path: string;
  readonly timestamp: string;
  /** Only populated for validation errors; never exposes internals. */
  readonly details?: unknown;
}

/**
 * Global exception filter.
 *
 * Converts every thrown error into a consistent, safe JSON envelope. Internal
 * error details and stack traces are logged but NEVER returned to the client in
 * production, satisfying the "never expose internal errors" requirement.
 */
@Catch()
export class AllExceptionsFilter implements ExceptionFilter {
  constructor(
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
    private readonly configService: AppConfigService,
  ) {}

  catch(exception: unknown, host: ArgumentsHost): void {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    const { status, errorCode, message, details } = this.resolveException(exception);

    const body: ErrorResponseBody = {
      statusCode: status,
      errorCode,
      message,
      path: request.url,
      timestamp: new Date().toISOString(),
      ...(details !== undefined ? { details } : {}),
    };

    this.logException(exception, status, request);

    response.status(status).json(body);
  }

  /** Normalise any thrown value into a safe, client-facing error descriptor. */
  private resolveException(exception: unknown): {
    status: number;
    errorCode: string;
    message: string;
    details?: unknown;
  } {
    if (exception instanceof DomainException) {
      return {
        status: exception.getStatus(),
        errorCode: exception.errorCode,
        message: exception.message,
        details: (exception as { details?: unknown }).details,
      };
    }

    if (exception instanceof HttpException) {
      const status = exception.getStatus();
      const responseBody = exception.getResponse();
      const message =
        typeof responseBody === 'string'
          ? responseBody
          : ((responseBody as { message?: string | string[] }).message ?? exception.message);
      return {
        status,
        errorCode: this.statusToErrorCode(status),
        message: Array.isArray(message) ? message.join('; ') : message,
      };
    }

    // Unknown / unexpected error — hide everything behind a generic message.
    return {
      status: HttpStatus.INTERNAL_SERVER_ERROR,
      errorCode: ErrorCode.InternalError,
      message: this.configService.isProduction
        ? 'Internal server error'
        : exception instanceof Error
          ? exception.message
          : String(exception),
    };
  }

  private statusToErrorCode(status: number): string {
    if (status === HttpStatus.NOT_FOUND) {
      return ErrorCode.EntityNotFound;
    }
    if (status === HttpStatus.BAD_REQUEST) {
      return ErrorCode.ValidationFailed;
    }
    if (status === HttpStatus.UNAUTHORIZED) {
      return ErrorCode.WebhookUnauthorized;
    }
    return `HTTP_${status}`;
  }

  private logException(exception: unknown, status: number, request: Request): void {
    const context = AllExceptionsFilter.name;
    const meta = `${request.method} ${request.url} -> ${status}`;

    if (status >= HttpStatus.INTERNAL_SERVER_ERROR) {
      this.logger.error(
        meta,
        exception instanceof Error ? exception.stack : String(exception),
        context,
      );
    } else {
      this.logger.warn(
        `${meta} :: ${exception instanceof Error ? exception.message : String(exception)}`,
        context,
      );
    }
  }
}
