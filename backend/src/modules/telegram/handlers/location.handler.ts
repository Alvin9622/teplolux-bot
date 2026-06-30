import { Injectable } from '@nestjs/common';
import { BotCommand, BotCommandName } from '../constants/commands.constants';
import { BotMessage } from '../constants/messages.constants';
import { CompanyLocation } from '../constants/company.constants';
import { Keyboards } from '../keyboards/main-menu.keyboard';
import { TelegramResponderService } from '../services/telegram-responder.service';
import { CommandHandler } from './command-handler.interface';
import { HandlerContext } from './handler-context';

/** Handles `/location`: sends a textual intro followed by a location pin. */
@Injectable()
export class LocationCommandHandler implements CommandHandler {
  readonly command: BotCommandName = BotCommand.Location;

  constructor(private readonly responder: TelegramResponderService) {}

  async handle(context: HandlerContext): Promise<void> {
    await this.responder.sendText(context, BotMessage.location);
    await this.responder.sendLocation(
      context,
      CompanyLocation.latitude,
      CompanyLocation.longitude,
      Keyboards.backToMenu(),
    );
  }
}
