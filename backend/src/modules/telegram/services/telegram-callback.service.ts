import { Injectable } from '@nestjs/common';
import { I18nService } from '../../../i18n/i18n.service';
import { TKey } from '../../../i18n/i18n.keys';
import { Locale, TranslationKey } from '../../../i18n/i18n.types';
import { CallbackData, CallbackDataValue } from '../constants/callback-data.constants';
import { CompanyLocation } from '../constants/company.constants';
import { escapeHtml } from '../constants/messages.constants';
import { Keyboards } from '../keyboards/main-menu.keyboard';
import { TelegramResponderService } from './telegram-responder.service';
import { TelegramUserService } from './telegram-user.service';
import { HandlerContext } from '../handlers/handler-context';

/**
 * Routes inline-keyboard callback presses to their (localised) responses.
 *
 * Every callback EDITS the message the user pressed (rather than sending a new
 * one), and all copy is resolved through {@link I18nService} in the user's
 * locale. Language selection / change is handled here too. Kept separate from
 * command handlers so the menu/navigation layer can evolve independently.
 */
@Injectable()
export class TelegramCallbackService {
  /** Simple "show a translated text screen with a back button" callbacks. */
  private readonly textRoutes: ReadonlyMap<CallbackDataValue, TranslationKey>;

  constructor(
    private readonly responder: TelegramResponderService,
    private readonly users: TelegramUserService,
    private readonly i18n: I18nService,
  ) {
    this.textRoutes = new Map<CallbackDataValue, TranslationKey>([
      [CallbackData.Boilers, TKey.categoryBoilers],
      [CallbackData.Radiators, TKey.categoryRadiators],
      [CallbackData.FloorHeating, TKey.categoryFloorHeating],
      [CallbackData.Service, TKey.service],
      [CallbackData.Dealer, TKey.dealer],
      [CallbackData.Operator, TKey.operator],
      [CallbackData.Contact, TKey.contact],
    ]);
  }

  /**
   * Handle an inline-button press. Returns true when the callback was
   * recognised and handled.
   */
  async handle(context: HandlerContext, data: string): Promise<boolean> {
    // Open the language selection screen.
    if (data === CallbackData.ChangeLanguage) {
      await this.responder.editText(
        context,
        this.i18n.t(context.locale, TKey.languagePrompt),
        Keyboards.languageSelection(),
      );
      return true;
    }

    // Apply a language selection, persist it and show the localised main menu.
    if (data === CallbackData.SelectLangUz || data === CallbackData.SelectLangRu) {
      const locale: Locale = data === CallbackData.SelectLangRu ? 'ru' : 'uz';
      await this.users.setLanguage(context.user.id, locale);
      await this.showMainMenu(context, locale);
      return true;
    }

    // Back to the personalised main menu (in the current locale).
    if (data === CallbackData.BackToMenu) {
      await this.showMainMenu(context, context.locale);
      return true;
    }

    // Location — edited in place (with a maps link) to keep the
    // "edit the current message" behaviour for every button.
    if (data === CallbackData.Location) {
      await this.responder.editText(
        context,
        this.i18n.t(context.locale, TKey.locationDetail, {
          lat: CompanyLocation.latitude,
          lng: CompanyLocation.longitude,
        }),
        Keyboards.backToMenu(this.i18n.scoped(context.locale)),
      );
      return true;
    }

    const key = this.textRoutes.get(data as CallbackDataValue);
    if (!key) {
      return false;
    }
    await this.responder.editText(
      context,
      this.i18n.t(context.locale, key),
      Keyboards.backToMenu(this.i18n.scoped(context.locale)),
    );
    return true;
  }

  /** Edit the current message into the personalised, localised main menu. */
  private async showMainMenu(context: HandlerContext, locale: Locale): Promise<void> {
    await this.responder.editText(
      context,
      this.i18n.t(locale, TKey.welcome, { name: escapeHtml(context.user.firstName ?? '') }),
      Keyboards.mainMenu(this.i18n.scoped(locale)),
    );
  }
}
