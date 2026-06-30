import { Module } from '@nestjs/common';
import { TelegramWebhookController } from './controllers/telegram-webhook.controller';
import { COMMAND_HANDLERS, CommandHandler } from './handlers/command-handler.interface';
import { CatalogCommandHandler } from './handlers/catalog.handler';
import { ContactCommandHandler } from './handlers/contact.handler';
import { DealerCommandHandler } from './handlers/dealer.handler';
import { HelpCommandHandler } from './handlers/help.handler';
import { LocationCommandHandler } from './handlers/location.handler';
import { OperatorCommandHandler } from './handlers/operator.handler';
import { ServiceCommandHandler } from './handlers/service.handler';
import { StartCommandHandler } from './handlers/start.handler';
import { ChatMessageRepository } from './repositories/chat-message.repository';
import { TelegramUserRepository } from './repositories/telegram-user.repository';
import { TelegramApiService } from './services/telegram-api.service';
import { TelegramCallbackService } from './services/telegram-callback.service';
import { TelegramResponderService } from './services/telegram-responder.service';
import { TelegramUpdateService } from './services/telegram-update.service';
import { TelegramUserService } from './services/telegram-user.service';

/** Concrete command handler providers, registered individually for DI. */
const commandHandlerProviders = [
  StartCommandHandler,
  HelpCommandHandler,
  CatalogCommandHandler,
  ServiceCommandHandler,
  DealerCommandHandler,
  OperatorCommandHandler,
  ContactCommandHandler,
  LocationCommandHandler,
];

/**
 * Telegram channel module.
 *
 * Self-contained vertical slice (controller → services → repositories) that can
 * later be extracted into its own microservice. Relies on the global database,
 * Redis, config and logging modules.
 */
@Module({
  controllers: [TelegramWebhookController],
  providers: [
    // Repositories
    TelegramUserRepository,
    ChatMessageRepository,
    // Services
    TelegramApiService,
    TelegramUserService,
    TelegramResponderService,
    TelegramCallbackService,
    TelegramUpdateService,
    // Command handlers (individual)
    ...commandHandlerProviders,
    // Aggregate the handlers behind the COMMAND_HANDLERS token for the dispatcher.
    {
      provide: COMMAND_HANDLERS,
      useFactory: (...handlers: CommandHandler[]): CommandHandler[] => handlers,
      inject: commandHandlerProviders,
    },
  ],
  exports: [TelegramApiService, TelegramUpdateService],
})
export class TelegramModule {}
