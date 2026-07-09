import { envSchema, ValidatedEnv } from './env.validation';

/**
 * Strongly-typed, namespaced application configuration.
 *
 * Built once from the validated environment so the rest of the application
 * never touches `process.env` directly and always works with typed values.
 */
export interface AppConfig {
  readonly nodeEnv: ValidatedEnv['NODE_ENV'];
  readonly isProduction: boolean;
  readonly port: number;
  readonly apiPrefix: string;
  readonly baseUrl: string;
  readonly corsOrigins: string[] | boolean;
}

export interface LoggerConfig {
  readonly level: ValidatedEnv['LOG_LEVEL'];
  readonly toFile: boolean;
  readonly dir: string;
}

export interface DatabaseConfig {
  readonly url: string;
}

export interface RedisConfig {
  readonly host: string;
  readonly port: number;
  readonly password: string;
  readonly db: number;
}

export interface JwtConfig {
  readonly secret: string;
  readonly expiresIn: string;
}

export interface TelegramConfig {
  readonly botToken: string;
  readonly webhookSecret: string;
  readonly webhookPath: string;
  readonly setWebhookOnStartup: boolean;
  /** Group/channel chat id that receives every submitted lead. Empty = disabled. */
  readonly leadChatId: string;
}

export interface RateLimitConfig {
  readonly ttlMs: number;
  readonly max: number;
}

export interface Configuration {
  readonly app: AppConfig;
  readonly logger: LoggerConfig;
  readonly database: DatabaseConfig;
  readonly redis: RedisConfig;
  readonly jwt: JwtConfig;
  readonly telegram: TelegramConfig;
  readonly rateLimit: RateLimitConfig;
}

/** Top-level configuration namespace keys (used for typed lookups). */
export const CONFIG_NAMESPACE = 'configuration';

/**
 * Parse the CORS_ORIGINS string into a value accepted by the CORS middleware.
 * `*` means "allow any origin"; otherwise a comma-separated allow-list.
 */
function parseCorsOrigins(raw: string): string[] | boolean {
  const trimmed = raw.trim();
  if (trimmed === '*' || trimmed === '') {
    return true;
  }
  return trimmed
    .split(',')
    .map((origin) => origin.trim())
    .filter((origin) => origin.length > 0);
}

/**
 * Configuration factory registered with `@nestjs/config`.
 *
 * Re-parses `process.env` through {@link envSchema} so it works with fully
 * typed, coerced values (numbers as numbers, booleans as booleans). `@nestjs/config`
 * keeps raw strings in `process.env`, so parsing here — rather than reading the
 * raw values — is what guarantees correct types throughout the application.
 */
export function configurationFactory(): Configuration {
  const env: ValidatedEnv = envSchema.parse(process.env);

  return {
    app: {
      nodeEnv: env.NODE_ENV,
      isProduction: env.NODE_ENV === 'production',
      port: env.PORT,
      apiPrefix: env.API_PREFIX,
      baseUrl: env.APP_BASE_URL,
      corsOrigins: parseCorsOrigins(env.CORS_ORIGINS),
    },
    logger: {
      level: env.LOG_LEVEL,
      toFile: env.LOG_TO_FILE,
      dir: env.LOG_DIR,
    },
    database: {
      url: env.DATABASE_URL,
    },
    redis: {
      host: env.REDIS_HOST,
      port: env.REDIS_PORT,
      password: env.REDIS_PASSWORD,
      db: env.REDIS_DB,
    },
    jwt: {
      secret: env.JWT_SECRET,
      expiresIn: env.JWT_EXPIRES_IN,
    },
    telegram: {
      botToken: env.TELEGRAM_BOT_TOKEN,
      webhookSecret: env.TELEGRAM_WEBHOOK_SECRET,
      webhookPath: env.TELEGRAM_WEBHOOK_PATH,
      setWebhookOnStartup: env.TELEGRAM_SET_WEBHOOK_ON_STARTUP,
      leadChatId: env.TELEGRAM_LEAD_CHAT_ID,
    },
    rateLimit: {
      ttlMs: env.RATE_LIMIT_TTL_MS,
      max: env.RATE_LIMIT_MAX,
    },
  };
}
