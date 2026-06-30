import { Injectable } from '@nestjs/common';
import { TelegramUser as PersistedUser } from '@prisma/client';
import { TelegramUserRepository } from '../repositories/telegram-user.repository';
import { TelegramUser } from '../types/telegram-api.types';

/**
 * Application service orchestrating {@link TelegramUser} persistence.
 *
 * Sits between the dispatcher and the repository, exposing intent-revealing
 * operations and shielding callers from ORM details.
 */
@Injectable()
export class TelegramUserService {
  constructor(private readonly repository: TelegramUserRepository) {}

  /** Create or refresh the CRM record for an incoming Telegram user. */
  async upsertFromTelegram(user: TelegramUser): Promise<PersistedUser> {
    return this.repository.upsert({
      telegramId: user.id,
      username: user.username,
      firstName: user.first_name,
      lastName: user.last_name,
      languageCode: user.language_code,
    });
  }

  async setPhone(userId: string, phone: string): Promise<PersistedUser> {
    return this.repository.updatePhone(userId, phone);
  }
}
