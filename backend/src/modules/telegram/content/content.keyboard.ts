import { Translator } from '../../../i18n/i18n.types';
import { InlineKeyboardButton, InlineKeyboardMarkup } from '../types/telegram-api.types';
import { CallbackData } from '../constants/callback-data.constants';
import { ContentAction, contentPageCallback } from './content.constants';
import { ContentButton, ContentPage } from './content.types';

/** Map a single content button to its Telegram inline-keyboard button. */
function buildButton(
  t: Translator,
  page: ContentPage,
  button: ContentButton,
): InlineKeyboardButton {
  const text = t(button.labelKey);
  const { action } = button;

  switch (action.type) {
    case 'page':
      return { text, callback_data: contentPageCallback(action.pageId) };
    case 'flow':
      // Reuse the existing flow trigger; the conversation engine starts it.
      return { text, callback_data: action.trigger };
    case 'url':
      return { text, url: action.url };
    case 'phone':
      return { text, callback_data: `${ContentAction.PhonePrefix}${action.phone}` };
    case 'mainMenu':
      // Reuse the existing "back to main menu" callback (rendered by the menu layer).
      return { text, callback_data: CallbackData.BackToMenu };
    case 'back':
      return {
        text,
        callback_data: page.parentId ? contentPageCallback(page.parentId) : CallbackData.BackToMenu,
      };
    default: {
      const exhaustive: never = action;
      throw new Error(`Unhandled content button action: ${JSON.stringify(exhaustive)}`);
    }
  }
}

/** Build the inline keyboard for a content page from its declarative buttons. */
export function buildContentKeyboard(t: Translator, page: ContentPage): InlineKeyboardMarkup {
  return {
    inline_keyboard: page.buttons.map((row) => row.map((button) => buildButton(t, page, button))),
  };
}
