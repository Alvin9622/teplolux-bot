import { ArgumentMetadata, Injectable, PipeTransform } from '@nestjs/common';
import { ZodSchema } from 'zod';
import { ValidationException } from '../exceptions';

/**
 * Validates and parses incoming payloads against a Zod schema.
 *
 * Returns the typed, parsed value on success and throws a
 * {@link ValidationException} (HTTP 400) with structured issue details on
 * failure. Use via `new ZodValidationPipe(schema)` on a route parameter.
 */
@Injectable()
export class ZodValidationPipe<T> implements PipeTransform<unknown, T> {
  constructor(private readonly schema: ZodSchema<T>) {}

  transform(value: unknown, _metadata: ArgumentMetadata): T {
    const result = this.schema.safeParse(value);
    if (!result.success) {
      throw new ValidationException(
        'Request payload validation failed',
        result.error.issues.map((issue) => ({
          path: issue.path.join('.'),
          message: issue.message,
        })),
      );
    }
    return result.data;
  }
}
