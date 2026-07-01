import { Injectable } from '@nestjs/common';
import { RedisService } from '../../../redis/redis.service';
import { CONVERSATION_REDIS_PREFIX, CONVERSATION_TTL_SECONDS } from './conversation.constants';
import { ConversationState } from './conversation.types';

/**
 * Redis-backed store for transient conversation state.
 *
 * Keeping flow state in Redis (rather than the database) makes it naturally
 * ephemeral — it expires automatically and requires no schema change — while
 * still surviving across the stateless webhook requests that drive the bot.
 */
@Injectable()
export class ConversationStateStore {
  constructor(private readonly redis: RedisService) {}

  private key(telegramId: bigint | number): string {
    return `${CONVERSATION_REDIS_PREFIX}${telegramId.toString()}`;
  }

  async get(telegramId: bigint | number): Promise<ConversationState | null> {
    const raw = await this.redis.instance.get(this.key(telegramId));
    return raw ? (JSON.parse(raw) as ConversationState) : null;
  }

  async set(telegramId: bigint | number, state: ConversationState): Promise<void> {
    await this.redis.instance.set(
      this.key(telegramId),
      JSON.stringify(state),
      'EX',
      CONVERSATION_TTL_SECONDS,
    );
  }

  async clear(telegramId: bigint | number): Promise<void> {
    await this.redis.instance.del(this.key(telegramId));
  }
}
