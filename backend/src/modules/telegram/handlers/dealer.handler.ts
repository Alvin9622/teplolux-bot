import { Injectable } from '@nestjs/common';
import { BotCommand, BotCommandName } from '../constants/commands.constants';
import { BotMessage } from '../constants/messages.constants';
import { Keyboards } from '../keyboards/main-menu.keyboard';
import { TelegramResponderService } from '../services/telegram-responder.service';
import { CommandHandler } from './command-handler.interface';
import { HandlerContext } from './handler-context';

/** Handles `/dealer`: begins the "become a dealer" partnership flow. */
@Injectable()
export class DealerCommandHandler implements CommandHandler {
  readonly command: BotCommandName = BotCommand.Dealer;

  constructor(private readonly responder: TelegramResponderService) {}

  async handle(context: HandlerContext): Promise<void> {
    await this.responder.sendText(context, BotMessage.dealer, Keyboards.backToMenu());
  }
}
