import { InlineKeyboardMarkup } from '../types/telegram-api.types';
import { CallbackData } from '../constants/callback-data.constants';
import { contentPageCallback, ContentPageId } from '../content/content.constants';
import { pnavCallback, PRODUCT_ROOT_ID } from '../content/product-tree';
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
  /**
   * Primary menu shown on /start and when returning to the menu.
   *
   * Deliberately limited to the six top-level actions. Products / Contacts /
   * About open informational content pages (no lead flow); Service, Become
   * Dealer and Contact Operator start the existing Contact Request flow.
   */
  mainMenu(t: Translator): InlineKeyboardMarkup {
    return {
      inline_keyboard: [
        [
          {
            // Products now opens the hierarchical Product Navigator (tree-driven).
            text: t(TKey.menuProducts),
            callback_data: pnavCallback(PRODUCT_ROOT_ID),
          },
        ],
        [
          { text: t(TKey.menuService), callback_data: CallbackData.Service },
          { text: t(TKey.menuDealer), callback_data: CallbackData.Dealer },
        ],
        [
          {
            text: t(TKey.menuContacts),
            callback_data: contentPageCallback(ContentPageId.Contacts),
          },
          { text: t(TKey.menuAbout), callback_data: contentPageCallback(ContentPageId.About) },
        ],
        [{ text: t(TKey.menuOperator), callback_data: CallbackData.Operator }],
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
