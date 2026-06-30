import { Inject, Injectable, LoggerService } from '@nestjs/common';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { LogEvent } from '../../../logger/log-events';
import { I18nService } from '../../../i18n/i18n.service';
import { TKey } from '../../../i18n/i18n.keys';
import { BotCommand, BotCommandName } from '../constants/commands.constants';
import { escapeHtml } from '../constants/messages.constants';
import { Keyboards } from '../keyboards/main-menu.keyboard';
import { TelegramResponderService } from '../services/telegram-responder.service';
import { CommandHandler } from './command-handler.interface';
import { HandlerContext } from './handler-context';

/**
 * Handles `/start`.
 *
 * On first contact (no language selected yet) it shows the language selection
 * screen. Once a language is set it greets the user and presents the localised
 * main inline menu — so the selection step is skipped on subsequent starts.
 */
@Injectable()
export class StartCommandHandler implements CommandHandler {
  readonly command: BotCommandName = BotCommand.Start;

  constructor(
    private readonly responder: TelegramResponderService,
    private readonly i18n: I18nService,
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
  ) {}

  async handle(context: HandlerContext): Promise<void> {
    this.logger.log(
      `${LogEvent.UserStartedBot}: ${context.user.telegramId}`,
      StartCommandHandler.name,
    );

    // First-time user: prompt for a language before anything else.
    if (context.user.language === null) {
      await this.responder.sendText(
        context,
        this.i18n.t(context.locale, TKey.languagePrompt),
        Keyboards.languageSelection(),
      );
      return;
    }

    await this.responder.sendText(
      context,
      this.i18n.t(context.locale, TKey.welcome, {
        name: escapeHtml(context.user.firstName ?? ''),
      }),
      Keyboards.mainMenu(this.i18n.scoped(context.locale)),
    );
  }
}
