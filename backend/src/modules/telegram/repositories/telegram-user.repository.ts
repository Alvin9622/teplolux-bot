import { Injectable } from '@nestjs/common';
import { Prisma, TelegramUser } from '@prisma/client';
import { PrismaService } from '../../../database/prisma.service';

/** Fields used to create or update a Telegram user from an incoming update. */
export interface UpsertTelegramUserInput {
  telegramId: number;
  username?: string | null;
  firstName?: string | null;
  lastName?: string | null;
  languageCode?: string | null;
}

/**
 * Data-access layer for {@link TelegramUser}.
 *
 * Implements the Repository pattern: encapsulates all Prisma queries for the
 * entity so services depend on an intent-revealing interface, not the ORM.
 */
@Injectable()
export class TelegramUserRepository {
  constructor(private readonly prisma: PrismaService) {}

  /**
   * Insert the user on first contact or refresh their profile + activity on
   * subsequent contact. Returns the persisted entity.
   */
  async upsert(input: UpsertTelegramUserInput): Promise<TelegramUser> {
    const telegramId = BigInt(input.telegramId);
    const now = new Date();
    const profile = {
      username: input.username ?? null,
      firstName: input.firstName ?? null,
      lastName: input.lastName ?? null,
      languageCode: input.languageCode ?? null,
    };

    return this.prisma.telegramUser.upsert({
      where: { telegramId },
      create: { telegramId, ...profile, lastActivity: now },
      update: { ...profile, lastActivity: now },
    });
  }

  async findByTelegramId(telegramId: number): Promise<TelegramUser | null> {
    return this.prisma.telegramUser.findUnique({
      where: { telegramId: BigInt(telegramId) },
    });
  }

  async updatePhone(id: string, phone: string): Promise<TelegramUser> {
    return this.prisma.telegramUser.update({
      where: { id },
      data: { phone },
    });
  }

  async touchActivity(id: string): Promise<void> {
    await this.prisma.telegramUser.update({
      where: { id },
      data: { lastActivity: new Date() },
    });
  }

  /** Escape hatch for advanced queries while keeping callers ORM-agnostic. */
  async count(where?: Prisma.TelegramUserWhereInput): Promise<number> {
    return this.prisma.telegramUser.count({ where });
  }
}
