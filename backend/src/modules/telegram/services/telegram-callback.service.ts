import { Injectable } from '@nestjs/common';
import { BotMessage } from '../constants/messages.constants';
import { CallbackData, CallbackDataValue } from '../constants/callback-data.constants';
import { CompanyLocation } from '../constants/company.constants';
import { Keyboards } from '../keyboards/main-menu.keyboard';
import { TelegramResponderService } from './telegram-responder.service';
import { HandlerContext } from '../handlers/handler-context';
import { InlineKeyboardMarkup } from '../types/telegram-api.types';

/** A static text response with an optional inline keyboard. */
interface CallbackResponse {
  readonly text: string;
  readonly keyboard?: InlineKeyboardMarkup;
}

/**
 * Routes inline-keyboard callback presses to their responses.
 *
 * Kept separate from command handlers so the menu/navigation layer can evolve
 * independently. Unknown callbacks fall back to the main menu.
 */
@Injectable()
export class TelegramCallbackService {
  private readonly routes: ReadonlyMap<CallbackDataValue, CallbackResponse>;

  constructor(private readonly responder: TelegramResponderService) {
    this.routes = new Map<CallbackDataValue, CallbackResponse>([
      [
        CallbackData.Boilers,
        { text: BotMessage.category.boilers, keyboard: Keyboards.backToMenu() },
      ],
      [
        CallbackData.Radiators,
        { text: BotMessage.category.radiators, keyboard: Keyboards.backToMenu() },
      ],
      [
        CallbackData.FloorHeating,
        { text: BotMessage.category.floorHeating, keyboard: Keyboards.backToMenu() },
      ],
      [CallbackData.Service, { text: BotMessage.service, keyboard: Keyboards.backToMenu() }],
      [CallbackData.Dealer, { text: BotMessage.dealer, keyboard: Keyboards.backToMenu() }],
      [CallbackData.Operator, { text: BotMessage.operator, keyboard: Keyboards.backToMenu() }],
      [CallbackData.Contact, { text: BotMessage.contact, keyboard: Keyboards.backToMenu() }],
      [CallbackData.BackToMenu, { text: BotMessage.catalogIntro, keyboard: Keyboards.mainMenu() }],
    ]);
  }

  /** Returns true when the callback was recognised and handled. */
  async handle(context: HandlerContext, data: string): Promise<boolean> {
    // Location is special — it sends an actual location pin, not just text.
    if (data === CallbackData.Location) {
      await this.responder.sendText(context, BotMessage.location);
      await this.responder.sendLocation(
        context,
        CompanyLocation.latitude,
        CompanyLocation.longitude,
        Keyboards.backToMenu(),
      );
      return true;
    }

    const response = this.routes.get(data as CallbackDataValue);
    if (!response) {
      return false;
    }
    await this.responder.sendText(context, response.text, response.keyboard);
    return true;
  }
}
