import { Inject, Injectable, LoggerService } from '@nestjs/common';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { I18nService } from '../../../i18n/i18n.service';
import { TKey } from '../../../i18n/i18n.keys';
import { Translator } from '../../../i18n/i18n.types';
import { CallbackData } from '../constants/callback-data.constants';
import { HandlerContext } from '../handlers/handler-context';
import { TelegramResponderService } from '../services/telegram-responder.service';
import { InlineKeyboardButton } from '../types/telegram-api.types';
import { operatorButton } from './content.navigation';
import {
  childCallback,
  findProductNode,
  hasChildren,
  parsePnav,
  pnavCallback,
  PRODUCT_NAV_PAGE_SIZE,
  productPageSlice,
  ProductNode,
} from './product-tree';

/**
 * Hierarchical Product Navigator (Products → Category → Subcategory → Actions).
 *
 * Data-driven by the reusable {@link PRODUCT_TREE}: intermediate nodes render a
 * paginated list of child buttons; leaf nodes render an action page. It REUSES
 * everything — message editing ({@link TelegramResponderService.editText}), the
 * shared operator button, the existing `content:page:*` callbacks (for leaves
 * that map to an existing rich page), the existing Request Price / operator flow
 * triggers, and the `nav:menu` main-menu callback. No page is replaced.
 */
@Injectable()
export class ProductNavigatorService {
  constructor(
    private readonly responder: TelegramResponderService,
    private readonly i18n: I18nService,
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
  ) {}

  /** Handle a `pnav:*` callback. Returns true when it was a navigator callback. */
  async handleCallback(context: HandlerContext, data: string): Promise<boolean> {
    const parsed = parsePnav(data);
    if (!parsed) {
      return false;
    }
    const node = findProductNode(parsed.nodeId);
    // Unknown node (e.g. tree changed) — recover gracefully to the root.
    const target = node ?? findProductNode('products');
    if (!target) {
      return false;
    }
    if (hasChildren(target)) {
      await this.renderLevel(context, target, parsed.page);
    } else {
      await this.renderActionPage(context, target);
    }
    return true;
  }

  /** Render an intermediate level: title/description + paginated child buttons. */
  private async renderLevel(
    context: HandlerContext,
    node: ProductNode,
    page: number,
  ): Promise<void> {
    const t = this.i18n.scoped(context.locale);
    const children = node.children ?? [];
    const slice = productPageSlice(children, page, PRODUCT_NAV_PAGE_SIZE);

    const rows: InlineKeyboardButton[][] = slice.items.map((child) => [
      { text: this.i18n.t(context.locale, child.titleKey), callback_data: childCallback(child) },
    ]);

    // Pagination controls only when there is more than one page.
    if (slice.pages > 1) {
      const controls: InlineKeyboardButton[] = [];
      if (slice.page > 0) {
        controls.push({
          text: t(TKey.contentButtonPrev),
          callback_data: pnavCallback(node.id, slice.page - 1),
        });
      }
      if (slice.page < slice.pages - 1) {
        controls.push({
          text: t(TKey.contentButtonNext),
          callback_data: pnavCallback(node.id, slice.page + 1),
        });
      }
      rows.push(controls);
    }

    rows.push(this.navRow(t, node));
    await this.responder.editText(context, this.body(context, node), { inline_keyboard: rows });
    this.logger.log(`Product level rendered: ${node.id} (page ${slice.page})`, 'ProductNavigator');
  }

  /** Render a leaf action page (Website / Catalog / Request Price / Specialist). */
  private async renderActionPage(context: HandlerContext, node: ProductNode): Promise<void> {
    const t = this.i18n.scoped(context.locale);
    const rows: InlineKeyboardButton[][] = [];

    // URL buttons are omitted while empty (architecture only — no URLs yet).
    if (node.websiteUrl) {
      rows.push([{ text: t(TKey.contentButtonWebsiteVisit), url: node.websiteUrl }]);
    }
    if (node.catalogUrl) {
      rows.push([{ text: t(TKey.contentButtonViewCatalog), url: node.catalogUrl }]);
    }
    // Request Price reuses the existing Contact Request flow trigger.
    if (node.priceTrigger) {
      rows.push([{ text: t(TKey.contentButtonRequestPrice), callback_data: node.priceTrigger }]);
    }
    // Contact Specialist reuses the existing operator flow (shared button).
    rows.push([operatorButton(t)]);
    rows.push(this.navRow(t, node));

    await this.responder.editText(context, this.body(context, node), { inline_keyboard: rows });
    this.logger.log(`Product action page rendered: ${node.id}`, 'ProductNavigator');
  }

  /** Title + short description; a friendly placeholder when there is no body. */
  private body(context: HandlerContext, node: ProductNode): string {
    const title = this.i18n.t(context.locale, node.titleKey);
    const description = node.descriptionKey
      ? this.i18n.t(context.locale, node.descriptionKey)
      : this.i18n.t(context.locale, TKey.contentEmptyState);
    return `<b>${title}</b>\n\n${description}`;
  }

  /** Consistent Back / Main Menu row — reuses shared labels + `nav:menu`. */
  private navRow(t: Translator, node: ProductNode): InlineKeyboardButton[] {
    const row: InlineKeyboardButton[] = [
      {
        text: t(TKey.contentButtonBack),
        // Back goes up one level, or to the main menu at the root.
        callback_data: node.parentId ? pnavCallback(node.parentId) : CallbackData.BackToMenu,
      },
    ];
    // Nested levels also offer a direct Main Menu jump (root omits it — no duplicate).
    if (node.parentId) {
      row.push({ text: t(TKey.contentButtonMainMenu), callback_data: CallbackData.BackToMenu });
    }
    return row;
  }
}
