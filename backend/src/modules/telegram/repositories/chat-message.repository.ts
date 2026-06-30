import { Injectable } from '@nestjs/common';
import { ChatMessage, MessageDirection, MessageStatus } from '@prisma/client';
import { PrismaService } from '../../../database/prisma.service';

/** Input describing a chat message to persist. */
export interface CreateChatMessageInput {
  telegramUserId: string;
  direction: MessageDirection;
  text?: string | null;
  telegramMessageId?: number | null;
  command?: string | null;
  status?: MessageStatus;
}

/**
 * Data-access layer for {@link ChatMessage}.
 *
 * Persists the full inbound/outbound conversation history that downstream CRM,
 * analytics and AI modules will consume.
 */
@Injectable()
export class ChatMessageRepository {
  constructor(private readonly prisma: PrismaService) {}

  async create(input: CreateChatMessageInput): Promise<ChatMessage> {
    return this.prisma.chatMessage.create({
      data: {
        telegramUserId: input.telegramUserId,
        direction: input.direction,
        text: input.text ?? null,
        telegramMessageId: input.telegramMessageId != null ? BigInt(input.telegramMessageId) : null,
        command: input.command ?? null,
        status: input.status ?? MessageStatus.RECEIVED,
      },
    });
  }

  async findRecentForUser(telegramUserId: string, take = 50): Promise<ChatMessage[]> {
    return this.prisma.chatMessage.findMany({
      where: { telegramUserId },
      orderBy: { createdAt: 'desc' },
      take,
    });
  }
}
