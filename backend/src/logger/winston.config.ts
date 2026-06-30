import { join } from 'node:path';
import { utilities as nestWinstonUtilities } from 'nest-winston';
import * as winston from 'winston';
import 'winston-daily-rotate-file';
import { LoggerConfig } from '../config/configuration';

const SERVICE_NAME = 'teplolux-crm';

/**
 * Build the array of Winston transports for the given logger configuration.
 *
 * - Console transport is always enabled with NestJS-friendly colourised output.
 * - When `toFile` is set, rotating JSON file transports are added for combined
 *   and error-only logs (production-grade, bounded disk usage).
 */
export function buildWinstonTransports(config: LoggerConfig): winston.transport[] {
  const transports: winston.transport[] = [
    new winston.transports.Console({
      level: config.level,
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.ms(),
        nestWinstonUtilities.format.nestLike(SERVICE_NAME, {
          colors: true,
          prettyPrint: true,
        }),
      ),
    }),
  ];

  if (config.toFile) {
    const fileFormat = winston.format.combine(
      winston.format.timestamp(),
      winston.format.errors({ stack: true }),
      winston.format.json(),
    );

    transports.push(
      new winston.transports.DailyRotateFile({
        level: config.level,
        dirname: config.dir,
        filename: join('combined-%DATE%.log'),
        datePattern: 'YYYY-MM-DD',
        zippedArchive: true,
        maxSize: '20m',
        maxFiles: '14d',
        format: fileFormat,
      }),
      new winston.transports.DailyRotateFile({
        level: 'error',
        dirname: config.dir,
        filename: join('error-%DATE%.log'),
        datePattern: 'YYYY-MM-DD',
        zippedArchive: true,
        maxSize: '20m',
        maxFiles: '30d',
        format: fileFormat,
      }),
    );
  }

  return transports;
}

/**
 * Assemble the full Winston logger options for {@link WinstonModule}.
 */
export function buildWinstonOptions(config: LoggerConfig): winston.LoggerOptions {
  return {
    level: config.level,
    defaultMeta: { service: SERVICE_NAME },
    transports: buildWinstonTransports(config),
  };
}
