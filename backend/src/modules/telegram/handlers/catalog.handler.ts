import { Injectable } from '@nestjs/common';
import { I18nService } from '../../../i18n/i18n.service';
import { TKey } from '../../../i18n/i18n.keys';
import { BotCommand, BotCommandName } from '../constants/commands.constants';
import { Keyboards } from '../keyboards/main-menu.keyboard';
import { TelegramResponderService } from '../services/telegram-responder.service';
import { CommandHandler } from './command-handler.interface';
import { HandlerContext } from './handler-context';

/** Handles `/catalog`: opens the product catalog with category buttons. */
@Injectable()
export class CatalogCommandHandler implements CommandHandler {
  readonly command: BotCommandName = BotCommand.Catalog;

  constructor(
    private readonly responder: TelegramResponderService,
    private readonly i18n: I18nService,
  ) {}

  async handle(context: HandlerContext): Promise<void> {
    await this.responder.sendText(
      context,
      this.i18n.t(context.locale, TKey.catalogIntro),
      Keyboards.mainMenu(this.i18n.scoped(context.locale)),
    );
  }
}
