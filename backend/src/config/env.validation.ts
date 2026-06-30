import { z } from 'zod';

/**
 * Zod schema describing every environment variable the application consumes.
 *
 * The schema is the single source of truth for configuration: it coerces raw
 * strings into typed values and enforces invariants. If validation fails the
 * application must NOT start (see {@link validateEnv}).
 */
export const envSchema = z.object({
  // Application
  NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
  PORT: z.coerce.number().int().positive().max(65535).default(3000),
  API_PREFIX: z.string().min(1).default('api'),
  APP_BASE_URL: z.string().url(),
  CORS_ORIGINS: z.string().default('*'),

  // Logging
  LOG_LEVEL: z.enum(['error', 'warn', 'info', 'http', 'debug', 'verbose']).default('info'),
  LOG_TO_FILE: z
    .enum(['true', 'false'])
    .transform((value) => value === 'true')
    .default('true'),
  LOG_DIR: z.string().min(1).default('logs'),

  // Database
  DATABASE_URL: z.string().url(),

  // Redis
  REDIS_HOST: z.string().min(1).default('localhost'),
  REDIS_PORT: z.coerce.number().int().positive().max(65535).default(6379),
  REDIS_PASSWORD: z.string().optional().default(''),
  REDIS_DB: z.coerce.number().int().min(0).max(15).default(0),

  // Auth
  JWT_SECRET: z.string().min(32, 'JWT_SECRET must be at least 32 characters'),
  JWT_EXPIRES_IN: z.string().min(1).default('1d'),

  // Telegram
  TELEGRAM_BOT_TOKEN: z
    .string()
    .regex(/^\d+:[\w-]+$/, 'TELEGRAM_BOT_TOKEN must look like "<id>:<secret>"'),
  TELEGRAM_WEBHOOK_SECRET: z
    .string()
    .min(1)
    .max(256)
    .regex(/^[A-Za-z0-9_-]+$/, 'TELEGRAM_WEBHOOK_SECRET may only contain A-Z, a-z, 0-9, _ and -'),
  TELEGRAM_WEBHOOK_PATH: z.string().min(1).default('webhook/telegram'),
  TELEGRAM_SET_WEBHOOK_ON_STARTUP: z
    .enum(['true', 'false'])
    .transform((value) => value === 'true')
    .default('false'),

  // Rate limiting
  RATE_LIMIT_TTL_MS: z.coerce.number().int().positive().default(60_000),
  RATE_LIMIT_MAX: z.coerce.number().int().positive().default(120),
});

/** Fully validated and typed environment. */
export type ValidatedEnv = z.infer<typeof envSchema>;

/**
 * Validate `process.env` against {@link envSchema}.
 *
 * Used as the `validate` hook of `@nestjs/config`'s `ConfigModule`, which calls
 * it during module initialisation. Throwing here aborts the bootstrap, fulfilling
 * the "application must not start if configuration is invalid" requirement.
 */
export function validateEnv(config: Record<string, unknown>): ValidatedEnv {
  const result = envSchema.safeParse(config);

  if (!result.success) {
    const issues = result.error.issues
      .map((issue) => `  - ${issue.path.join('.') || '(root)'}: ${issue.message}`)
      .join('\n');
    throw new Error(`Invalid environment configuration. The application cannot start.\n${issues}`);
  }

  return result.data;
}
