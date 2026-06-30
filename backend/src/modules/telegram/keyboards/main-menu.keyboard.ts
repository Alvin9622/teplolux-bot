import { InlineKeyboardMarkup } from '../types/telegram-api.types';
import { CallbackData } from '../constants/callback-data.constants';
import { TKey } from '../../../i18n/i18n.keys';
import { Translator } from '../../../i18n/i18n.types';

/**
 * Inline keyboard factories.
 *
 * The platform uses inline keyboards exclusively (per product requirements).
 * Button labels are translated via the locale-bound {@link Translator} passed
 * in by the caller, keeping markup construction free of hardcoded strings.
 */
export const Keyboards = {
  /** Primary menu shown on /start and when returning to the menu. */
  mainMenu(t: Translator): InlineKeyboardMarkup {
    return {
      inline_keyboard: [
        [
          { text: t(TKey.menuBoilers), callback_data: CallbackData.Boilers },
          { text: t(TKey.menuRadiators), callback_data: CallbackData.Radiators },
        ],
        [{ text: t(TKey.menuFloorHeating), callback_data: CallbackData.FloorHeating }],
        [
          { text: t(TKey.menuService), callback_data: CallbackData.Service },
          { text: t(TKey.menuDealer), callback_data: CallbackData.Dealer },
        ],
        [{ text: t(TKey.menuOperator), callback_data: CallbackData.Operator }],
        [
          { text: t(TKey.menuContact), callback_data: CallbackData.Contact },
          { text: t(TKey.menuLocation), callback_data: CallbackData.Location },
        ],
        [{ text: t(TKey.menuChangeLanguage), callback_data: CallbackData.ChangeLanguage }],
      ],
    };
  },

  /** Single "back to menu" button appended to drill-down screens. */
  backToMenu(t: Translator): InlineKeyboardMarkup {
    return {
      inline_keyboard: [[{ text: t(TKey.menuBack), callback_data: CallbackData.BackToMenu }]],
    };
  },

  /**
   * Language selection keyboard. Labels are the native language names, so this
   * keyboard is intentionally locale-independent (shown before a language is
   * chosen and when changing it).
   */
  languageSelection(): InlineKeyboardMarkup {
    return {
      inline_keyboard: [
        [{ text: "🇺🇿 O'zbekcha", callback_data: CallbackData.SelectLangUz }],
        [{ text: '🇷🇺 Русский', callback_data: CallbackData.SelectLangRu }],
      ],
    };
  },
} as const;
