import {
  CallHandler,
  ExecutionContext,
  Inject,
  Injectable,
  LoggerService,
  NestInterceptor,
} from '@nestjs/common';
import { Request, Response } from 'express';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';

/**
 * Logs every HTTP request/response pair with its latency.
 *
 * Provides structured observability for all inbound traffic (including the
 * Telegram webhook) without coupling controllers to logging concerns.
 */
@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  constructor(@Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService) {}

  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    if (context.getType() !== 'http') {
      return next.handle();
    }

    const http = context.switchToHttp();
    const request = http.getRequest<Request>();
    const response = http.getResponse<Response>();
    const { method, url } = request;
    const startedAt = Date.now();

    return next.handle().pipe(
      tap({
        next: () => {
          const elapsed = Date.now() - startedAt;
          this.logger.log(
            `${method} ${url} ${response.statusCode} +${elapsed}ms`,
            LoggingInterceptor.name,
          );
        },
        error: () => {
          const elapsed = Date.now() - startedAt;
          this.logger.warn(`${method} ${url} errored +${elapsed}ms`, LoggingInterceptor.name);
        },
      }),
    );
  }
}
