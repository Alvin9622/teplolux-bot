import { validateEnv } from './env.validation';

/** A complete, valid environment used as the baseline for each test. */
function validEnv(): Record<string, string> {
  return {
    NODE_ENV: 'test',
    PORT: '3000',
    API_PREFIX: 'api',
    APP_BASE_URL: 'https://crm.example.com',
    CORS_ORIGINS: '*',
    LOG_LEVEL: 'info',
    LOG_TO_FILE: 'false',
    LOG_DIR: 'logs',
    DATABASE_URL: 'postgresql://user:pass@localhost:5432/db?schema=public',
    REDIS_HOST: 'localhost',
    REDIS_PORT: '6379',
    REDIS_PASSWORD: '',
    REDIS_DB: '0',
    JWT_SECRET: 'a-very-long-and-secure-jwt-secret-value-1234',
    JWT_EXPIRES_IN: '1d',
    TELEGRAM_BOT_TOKEN: '123456789:AA_valid-token_value',
    TELEGRAM_WEBHOOK_SECRET: 'super-secret-webhook-token',
    TELEGRAM_WEBHOOK_PATH: 'webhook/telegram',
    TELEGRAM_SET_WEBHOOK_ON_STARTUP: 'false',
    RATE_LIMIT_TTL_MS: '60000',
    RATE_LIMIT_MAX: '120',
  };
}

describe('validateEnv', () => {
  it('parses and coerces a valid environment', () => {
    const result = validateEnv(validEnv());
    expect(result.PORT).toBe(3000);
    expect(result.LOG_TO_FILE).toBe(false);
    expect(result.NODE_ENV).toBe('test');
  });

  it('throws when a required variable is missing', () => {
    const env = validEnv();
    delete (env as Record<string, unknown>).DATABASE_URL;
    expect(() => validateEnv(env)).toThrow(/DATABASE_URL/);
  });

  it('rejects a JWT secret shorter than 32 characters', () => {
    const env = { ...validEnv(), JWT_SECRET: 'too-short' };
    expect(() => validateEnv(env)).toThrow(/JWT_SECRET/);
  });

  it('rejects a malformed Telegram bot token', () => {
    const env = { ...validEnv(), TELEGRAM_BOT_TOKEN: 'not-a-valid-token' };
    expect(() => validateEnv(env)).toThrow(/TELEGRAM_BOT_TOKEN/);
  });

  it('rejects a webhook secret with illegal characters', () => {
    const env = { ...validEnv(), TELEGRAM_WEBHOOK_SECRET: 'has spaces!' };
    expect(() => validateEnv(env)).toThrow(/TELEGRAM_WEBHOOK_SECRET/);
  });
});
