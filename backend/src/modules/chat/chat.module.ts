import { Module } from '@nestjs/common';

/**
 * Chat module — ARCHITECTURE PLACEHOLDER.
 *
 * Reserved for the channel-agnostic conversation layer (routing, operator
 * handoff, AI assistant, unified inbox) built on the `Conversation` /
 * `ChatMessage` models. Today, conversation history is written by the Telegram
 * module directly. No behaviour is wired here yet.
 */
@Module({})
export class ChatModule {}
