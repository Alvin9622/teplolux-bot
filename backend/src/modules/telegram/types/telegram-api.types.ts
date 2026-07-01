/**
 * Minimal, strongly-typed subset of the Telegram Bot API object model.
 *
 * Only the fields the platform consumes are modelled. The shapes mirror the
 * official Bot API so they can be extended safely as new features are added.
 * @see https://core.telegram.org/bots/api
 */

export interface TelegramUser {
  id: number;
  is_bot: boolean;
  first_name?: string;
  last_name?: string;
  username?: string;
  language_code?: string;
}

export interface TelegramChat {
  id: number;
  type: 'private' | 'group' | 'supergroup' | 'channel';
  title?: string;
  username?: string;
  first_name?: string;
  last_name?: string;
}

export interface TelegramMessageEntity {
  type: string;
  offset: number;
  length: number;
}

export interface TelegramContact {
  phone_number: string;
  first_name: string;
  last_name?: string;
  user_id?: number;
}

export interface TelegramLocation {
  latitude: number;
  longitude: number;
}

export interface TelegramMessage {
  message_id: number;
  from?: TelegramUser;
  chat: TelegramChat;
  date: number;
  text?: string;
  entities?: TelegramMessageEntity[];
  contact?: TelegramContact;
  location?: TelegramLocation;
}

export interface TelegramCallbackQuery {
  id: string;
  from: TelegramUser;
  message?: TelegramMessage;
  data?: string;
}

export interface TelegramUpdate {
  update_id: number;
  message?: TelegramMessage;
  edited_message?: TelegramMessage;
  callback_query?: TelegramCallbackQuery;
}

// ---------------------------------------------------------------------------
// Outbound (request) types
// ---------------------------------------------------------------------------

export interface InlineKeyboardButton {
  text: string;
  callback_data?: string;
  url?: string;
}

export interface InlineKeyboardMarkup {
  inline_keyboard: InlineKeyboardButton[][];
}

/** A custom reply-keyboard button. `request_contact` asks for the user's phone. */
export interface KeyboardButton {
  text: string;
  request_contact?: boolean;
  request_location?: boolean;
}

export interface ReplyKeyboardMarkup {
  keyboard: KeyboardButton[][];
  resize_keyboard?: boolean;
  one_time_keyboard?: boolean;
  input_field_placeholder?: string;
}

/** Instructs Telegram to hide the current custom reply keyboard. */
export interface ReplyKeyboardRemove {
  remove_keyboard: true;
}

/** Any markup accepted by `sendMessage`'s `reply_markup`. */
export type ReplyMarkup = InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove;

export type ParseMode = 'HTML' | 'MarkdownV2' | 'Markdown';

export interface SendMessageOptions {
  parse_mode?: ParseMode;
  reply_markup?: ReplyMarkup;
  disable_web_page_preview?: boolean;
}

export interface SendLocationOptions {
  reply_markup?: InlineKeyboardMarkup;
}

export interface AnswerCallbackQueryOptions {
  text?: string;
  show_alert?: boolean;
}

/** A bot command published to Telegram's command menu via `setMyCommands`. */
export interface BotCommandDefinition {
  command: string;
  description: string;
}

/**
 * Result of the `getWebhookInfo` method — used to confirm Telegram can reach
 * the configured webhook endpoint.
 * @see https://core.telegram.org/bots/api#webhookinfo
 */
export interface TelegramWebhookInfo {
  url: string;
  has_custom_certificate: boolean;
  pending_update_count: number;
  ip_address?: string;
  last_error_date?: number;
  last_error_message?: string;
  max_connections?: number;
  allowed_updates?: string[];
}

/** Generic envelope returned by every Bot API method. */
export interface TelegramApiResponse<T> {
  ok: boolean;
  result?: T;
  description?: string;
  error_code?: number;
}
