import { InlineKeyboardMarkup } from '../types/telegram-api.types';
import { CallbackData } from '../constants/callback-data.constants';

/**
 * Inline keyboard factories.
 *
 * The platform uses inline keyboards exclusively (per product requirements).
 * Keeping markup construction here decouples handlers from layout concerns.
 */
export const Keyboards = {
  /** Primary menu shown on /start and when returning to the menu. */
  mainMenu(): InlineKeyboardMarkup {
    return {
      inline_keyboard: [
        [
          { text: '🏠 Boilers', callback_data: CallbackData.Boilers },
          { text: '🔥 Radiators', callback_data: CallbackData.Radiators },
        ],
        [{ text: '♨️ Floor Heating', callback_data: CallbackData.FloorHeating }],
        [
          { text: '🛠 Service', callback_data: CallbackData.Service },
          { text: '🤝 Become Dealer', callback_data: CallbackData.Dealer },
        ],
        [{ text: '👨 Contact Operator', callback_data: CallbackData.Operator }],
        [
          { text: '📞 Contact', callback_data: CallbackData.Contact },
          { text: '📍 Location', callback_data: CallbackData.Location },
        ],
      ],
    };
  },

  /** Single "back to menu" button appended to drill-down screens. */
  backToMenu(): InlineKeyboardMarkup {
    return {
      inline_keyboard: [[{ text: '⬅️ Back to menu', callback_data: CallbackData.BackToMenu }]],
    };
  },
} as const;
