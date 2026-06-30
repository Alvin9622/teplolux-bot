import { Inject, Injectable, LoggerService } from '@nestjs/common';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { LogEvent } from '../../../logger/log-events';
import { BotCommand, BotCommandName } from '../constants/commands.constants';
import { BotMessage } from '../constants/messages.constants';
import { Keyboards } from '../keyboards/main-menu.keyboard';
import { TelegramResponderService } from '../services/telegram-responder.service';
import { CommandHandler } from './command-handler.interface';
import { HandlerContext } from './handler-context';

/** Handles `/start`: greets the user and presents the main inline menu. */
@Injectable()
export class StartCommandHandler implements CommandHandler {
  readonly command: BotCommandName = BotCommand.Start;

  constructor(
    private readonly responder: TelegramResponderService,
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
  ) {}

  async handle(context: HandlerContext): Promise<void> {
    this.logger.log(
      `${LogEvent.UserStartedBot}: ${context.user.telegramId}`,
      StartCommandHandler.name,
    );
    await this.responder.sendText(
      context,
      BotMessage.welcome(context.user.firstName ?? undefined),
      Keyboards.mainMenu(),
    );
  }
}
