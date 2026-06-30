import { Injectable } from '@nestjs/common';
import { I18nService } from '../../../i18n/i18n.service';
import { TKey } from '../../../i18n/i18n.keys';
import { BotCommand, BotCommandName } from '../constants/commands.constants';
import { CompanyLocation } from '../constants/company.constants';
import { Keyboards } from '../keyboards/main-menu.keyboard';
import { TelegramResponderService } from '../services/telegram-responder.service';
import { CommandHandler } from './command-handler.interface';
import { HandlerContext } from './handler-context';

/** Handles `/location`: sends a textual intro followed by a location pin. */
@Injectable()
export class LocationCommandHandler implements CommandHandler {
  readonly command: BotCommandName = BotCommand.Location;

  constructor(
    private readonly responder: TelegramResponderService,
    private readonly i18n: I18nService,
  ) {}

  async handle(context: HandlerContext): Promise<void> {
    await this.responder.sendText(context, this.i18n.t(context.locale, TKey.locationIntro));
    await this.responder.sendLocation(
      context,
      CompanyLocation.latitude,
      CompanyLocation.longitude,
      Keyboards.backToMenu(this.i18n.scoped(context.locale)),
    );
  }
}
