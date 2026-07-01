import { Injectable } from '@nestjs/common';
import { BotCommand, BotCommandName } from '../constants/commands.constants';
import { ConversationService } from '../conversation/conversation.service';
import { CommandHandler } from './command-handler.interface';
import { HandlerContext } from './handler-context';

/**
 * Handles `/cancel`: aborts any in-progress guided conversation and returns the
 * user to the main menu. Works at any point in a flow.
 */
@Injectable()
export class CancelCommandHandler implements CommandHandler {
  readonly command: BotCommandName = BotCommand.Cancel;

  constructor(private readonly conversation: ConversationService) {}

  async handle(context: HandlerContext): Promise<void> {
    await this.conversation.cancel(context);
  }
}
