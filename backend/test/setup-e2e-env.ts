/**
 * Populates a complete, valid environment before the application boots in e2e
 * tests. Real infrastructure (Postgres/Redis) is replaced with fakes in the
 * spec, so these values only need to satisfy configuration validation.
 */
export function applyTestEnv(): void {
  Object.assign(process.env, {
    NODE_ENV: 'test',
    PORT: '3000',
    API_PREFIX: 'api',
    APP_BASE_URL: 'https://crm.test.example.com',
    CORS_ORIGINS: '*',
    LOG_LEVEL: 'error',
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
    RATE_LIMIT_MAX: '1000',
  });
}
