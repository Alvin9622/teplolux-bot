import { Inject, Injectable, LoggerService } from '@nestjs/common';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { I18nService } from '../../../i18n/i18n.service';
import { TKey } from '../../../i18n/i18n.keys';
import { CallbackData } from '../constants/callback-data.constants';
import { escapeHtml } from '../constants/messages.constants';
import { contentPageCallback } from '../content/content.constants';
import { operatorButton } from '../content/content.navigation';
import { HandlerContext } from '../handlers/handler-context';
import { TelegramResponderService } from '../services/telegram-responder.service';
import { InlineKeyboardButton } from '../types/telegram-api.types';
import { Translator } from '../../../i18n/i18n.types';
import { faqAnswer, faqQuestion, FaqItem } from './faq.model';
import { FaqService } from './faq.service';
import {
  FaqAction,
  faqItemCallback,
  faqListCallback,
  isProductScope,
  PRODUCT_FAQ_IDS,
} from './faq.presentation';

/**
 * Renders the FAQ inside Telegram, reusing the existing {@link FaqService}
 * (no second FAQ implementation) and the shared message-editing + navigation
 * conventions. A "scope" is either a product category (curated subset) or a
 * plain FAQ category. Opened from product pages so each shows only its relevant
 * questions.
 */
@Injectable()
export class FaqPresenterService {
  constructor(
    private readonly faq: FaqService,
    private readonly responder: TelegramResponderService,
    private readonly i18n: I18nService,
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
  ) {}

  /** Handle a `faq:*` callback. Returns true when it was an FAQ callback. */
  async handleCallback(context: HandlerContext, data: string): Promise<boolean> {
    if (data.startsWith(FaqAction.ItemPrefix)) {
      const rest = data.slice(FaqAction.ItemPrefix.length);
      const sep = rest.indexOf(':');
      if (sep === -1) {
        return false;
      }
      await this.renderItem(context, rest.slice(0, sep), rest.slice(sep + 1));
      return true;
    }
    if (data.startsWith(FaqAction.ListPrefix)) {
      await this.renderList(context, data.slice(FaqAction.ListPrefix.length));
      return true;
    }
    return false;
  }

  /** FAQ items for a scope: a curated product subset, or a FAQ category. */
  private itemsForScope(scope: string): FaqItem[] {
    if (isProductScope(scope)) {
      return PRODUCT_FAQ_IDS.map((id) => this.faq.getItem(id)).filter(
        (item): item is FaqItem => item !== undefined,
      );
    }
    return this.faq.listItems(scope);
  }

  private async renderList(context: HandlerContext, scope: string): Promise<void> {
    const t = this.i18n.scoped(context.locale);
    const items = this.itemsForScope(scope);

    // Empty state: never a blank screen — show a friendly placeholder.
    const text = this.i18n.t(context.locale, items.length ? TKey.faqListTitle : TKey.faqEmpty);

    const rows: InlineKeyboardButton[][] = items.map((item) => [
      { text: faqQuestion(item, context.locale), callback_data: faqItemCallback(scope, item.id) },
    ]);
    rows.push([operatorButton(t)]);
    rows.push(this.backRow(t, this.listBackTarget(scope)));

    await this.responder.editText(context, text, { inline_keyboard: rows });
    this.logger.log(`FAQ list rendered: ${scope} (${items.length})`, FaqPresenterService.name);
  }

  private async renderItem(context: HandlerContext, scope: string, id: string): Promise<void> {
    const t = this.i18n.scoped(context.locale);
    const item = this.faq.getItem(id);
    // Unknown/expired item — recover gracefully by returning to the list.
    if (!item) {
      await this.renderList(context, scope);
      return;
    }

    const question = faqQuestion(item, context.locale);
    const answer = faqAnswer(item, context.locale);
    const text = `❓ <b>${escapeHtml(question)}</b>\n\n${escapeHtml(answer)}`;
    await this.responder.editText(context, text, {
      inline_keyboard: [[operatorButton(t)], this.backRow(t, faqListCallback(scope))],
    });
  }

  /** A consistent Back / Main Menu row (reuses the shared labels + callback). */
  private backRow(t: Translator, backCallback: string): InlineKeyboardButton[] {
    return [
      { text: t(TKey.contentButtonBack), callback_data: backCallback },
      { text: t(TKey.contentButtonMainMenu), callback_data: CallbackData.BackToMenu },
    ];
  }

  /** Back from a product FAQ returns to that product page; else the main menu. */
  private listBackTarget(scope: string): string {
    return isProductScope(scope)
      ? contentPageCallback(`product_${scope}`)
      : CallbackData.BackToMenu;
  }
}
