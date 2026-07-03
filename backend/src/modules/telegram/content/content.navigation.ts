import { TKey } from '../../../i18n/i18n.keys';
import { Translator } from '../../../i18n/i18n.types';
import { InlineKeyboardButton } from '../types/telegram-api.types';
import { CallbackData } from '../constants/callback-data.constants';
import { contentPageCallback } from './content.constants';
import { ContentPage, NavigationOptions } from './content.types';

/**
 * Reusable navigation footer for content pages.
 *
 * Instead of every page hand-authoring its own Back / Main Menu / Operator
 * buttons (inconsistent and duplicated), this builder appends ONE consistent
 * footer to every page. It reuses the existing callbacks — content page
 * navigation (`content:page:*`) and the main-menu callback (`nav:menu`) — and
 * the existing Contact Operator flow trigger, so routing is unchanged.
 */

/** Resolve the effective footer for a page: per-page override → smart default. */
function resolveNavigation(page: ContentPage): Required<NavigationOptions> {
  const nav = page.nav ?? {};
  return {
    back: nav.back ?? true,
    // Nested pages (with a parent) get a direct Main Menu jump; root pages omit
    // it because their Back already returns to the main menu — no duplicate.
    mainMenu: nav.mainMenu ?? page.parentId !== undefined,
    operator: nav.operator ?? true,
  };
}

/**
 * The single, reusable "Contact Operator" button — one action shared by every
 * page. Reuses the existing {@link CallbackData.Operator} flow trigger, so the
 * conversation engine starts the operator request exactly as it does from the
 * main menu. No page-specific operator handler is ever duplicated.
 */
export function operatorButton(t: Translator): InlineKeyboardButton {
  return { text: t(TKey.contentButtonOperator), callback_data: CallbackData.Operator };
}

/**
 * Build the consistent navigation rows for a page: an optional Operator row,
 * then a Back / Main Menu row (in that fixed order). Never emits an empty row.
 */
export function buildNavigationRows(t: Translator, page: ContentPage): InlineKeyboardButton[][] {
  const { back, mainMenu, operator } = resolveNavigation(page);
  const rows: InlineKeyboardButton[][] = [];

  if (operator) {
    rows.push([operatorButton(t)]);
  }

  const navRow: InlineKeyboardButton[] = [];
  if (back) {
    navRow.push({
      text: t(TKey.contentButtonBack),
      // Back returns to the parent page, or the main menu for a root page.
      callback_data: page.parentId ? contentPageCallback(page.parentId) : CallbackData.BackToMenu,
    });
  }
  if (mainMenu) {
    navRow.push({ text: t(TKey.contentButtonMainMenu), callback_data: CallbackData.BackToMenu });
  }
  if (navRow.length > 0) {
    rows.push(navRow);
  }

  return rows;
}
