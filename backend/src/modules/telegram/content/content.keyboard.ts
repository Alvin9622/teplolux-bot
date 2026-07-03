import { Translator } from '../../../i18n/i18n.types';
import { InlineKeyboardButton, InlineKeyboardMarkup } from '../types/telegram-api.types';
import { CallbackData } from '../constants/callback-data.constants';
import { ContentAction, contentPageCallback } from './content.constants';
import { buildNavigationRows } from './content.navigation';
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
    case 'callback':
      // Delegate to an existing callback handler (the content service ignores
      // non-`content:` callbacks, so it falls through to the menu layer).
      return { text, callback_data: action.data };
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

/**
 * Build the inline keyboard for a content page: the page's own buttons followed
 * by the consistent navigation footer (Back / Main Menu / Operator), so no page
 * hand-authors or duplicates those buttons.
 */
export function buildContentKeyboard(t: Translator, page: ContentPage): InlineKeyboardMarkup {
  const contentRows = page.buttons.map((row) => row.map((button) => buildButton(t, page, button)));
  return {
    inline_keyboard: [...contentRows, ...buildNavigationRows(t, page)],
  };
}
