import { z } from 'zod';

/**
 * Zod schema validating the structural integrity of an inbound Telegram update.
 *
 * It is intentionally permissive (`passthrough`) on nested objects so the bot
 * keeps working as Telegram adds fields, while still guaranteeing the shape the
 * dispatcher relies on (a numeric `update_id` plus at least one known payload).
 */
const telegramUserSchema = z
  .object({
    id: z.number(),
    is_bot: z.boolean(),
    first_name: z.string().optional(),
    last_name: z.string().optional(),
    username: z.string().optional(),
    language_code: z.string().optional(),
  })
  .passthrough();

const telegramChatSchema = z
  .object({
    id: z.number(),
    type: z.string(),
  })
  .passthrough();

const telegramMessageSchema = z
  .object({
    message_id: z.number(),
    date: z.number(),
    chat: telegramChatSchema,
    from: telegramUserSchema.optional(),
    text: z.string().optional(),
  })
  .passthrough();

const telegramCallbackQuerySchema = z
  .object({
    id: z.string(),
    from: telegramUserSchema,
    data: z.string().optional(),
    message: telegramMessageSchema.optional(),
  })
  .passthrough();

export const telegramUpdateSchema = z
  .object({
    update_id: z.number(),
    message: telegramMessageSchema.optional(),
    edited_message: telegramMessageSchema.optional(),
    callback_query: telegramCallbackQuerySchema.optional(),
  })
  .passthrough();

/** Validated update payload type. */
export type TelegramUpdateDto = z.infer<typeof telegramUpdateSchema>;
