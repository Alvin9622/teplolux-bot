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
    ]);
  }

  /**
   * Handle an inline-button press. Every callback EDITS the message the user
   * pressed (rather than sending a new one) so the conversation stays a single,
   * navigable screen. Returns true when the callback was recognised.
   */
  async handle(context: HandlerContext, data: string): Promise<boolean> {
    // "Back to main menu" — restore the personalised welcome + full menu.
    if (data === CallbackData.BackToMenu) {
      await this.responder.editText(
        context,
        BotMessage.welcome(context.user.firstName ?? undefined),
        Keyboards.mainMenu(),
      );
      return true;
    }

    // Location — edited in place (with a maps link) to honour the
    // "edit the current message" behaviour for every button.
    if (data === CallbackData.Location) {
      await this.responder.editText(
        context,
        BotMessage.locationDetail(CompanyLocation.latitude, CompanyLocation.longitude),
        Keyboards.backToMenu(),
      );
      return true;
    }

    const response = this.routes.get(data as CallbackDataValue);
    if (!response) {
      return false;
    }
    await this.responder.editText(context, response.text, response.keyboard);
    return true;
  }
}
