import { TelegramUser as PersistedUser } from '@prisma/client';
import { Locale } from '../../../i18n/i18n.types';
import { TelegramCallbackQuery, TelegramMessage } from '../types/telegram-api.types';

/**
 * Execution context passed to every command / callback handler.
 *
 * Carries the resolved chat, the persisted CRM user and the raw Telegram
 * payloads so handlers stay free of parsing and persistence concerns.
 */
export interface HandlerContext {
  /** Telegram chat id to reply to. */
  readonly chatId: number;
  /** The persisted CRM user (already upserted by the dispatcher). */
  readonly user: PersistedUser;
  /** Resolved interface locale for this interaction (selection or fallback). */
  readonly locale: Locale;
  /** Raw inbound message, when the update is a message. */
  readonly message?: TelegramMessage;
  /** Raw inbound callback query, when the update is an inline-button press. */
  readonly callbackQuery?: TelegramCallbackQuery;
  /** Free-text payload of the message (without the command), if any. */
  readonly text?: string;
}
