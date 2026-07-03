import { Inject, Injectable, LoggerService } from '@nestjs/common';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { LogEvent } from '../../../logger/log-events';
import { I18nService } from '../../../i18n/i18n.service';
import { TKey } from '../../../i18n/i18n.keys';
import { HandlerContext } from '../handlers/handler-context';
import { TelegramResponderService } from '../services/telegram-responder.service';
import { CompanyConfigService } from '../config/company-config.service';
import { KnowledgeService } from '../knowledge/knowledge.service';
import { ContentRegistry } from './content.registry';
import { ContentAction } from './content.constants';
import { buildContentKeyboard } from './content.keyboard';
import { ContentPage } from './content.types';

/**
 * Renders informational content pages dynamically from their declarative
 * {@link ContentPage} definitions.
 *
 * The service is data-driven: it never hardcodes page copy (all text comes from
 * i18n) and never hardcodes a specific page (all pages come from the
 * {@link ContentRegistry}). New pages need no changes here.
 */
@Injectable()
export class ContentService {
  constructor(
    private readonly registry: ContentRegistry,
    private readonly responder: TelegramResponderService,
    private readonly i18n: I18nService,
    private readonly companyConfig: CompanyConfigService,
    private readonly knowledge: KnowledgeService,
    @Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService,
  ) {}

  /** Returns true when the callback was a content-navigation callback. */
  async handleCallback(context: HandlerContext, data: string): Promise<boolean> {
    if (data.startsWith(ContentAction.PagePrefix)) {
      const pageId = data.slice(ContentAction.PagePrefix.length);
      const page = this.registry.get(pageId);
      if (!page) {
        return false;
      }
      await this.renderPage(context, page);
      return true;
    }

    if (data.startsWith(ContentAction.PhonePrefix)) {
      const phone = data.slice(ContentAction.PhonePrefix.length);
      await this.responder.sendText(
        context,
        this.i18n.t(context.locale, TKey.contentCallMessage, { phone }),
      );
      return true;
    }

    return false;
  }

  /**
   * Render a page: an optional image, an HTML `title + description` body, and an
   * inline keyboard built from the page's buttons. Text pages edit the current
   * message in place; pages with an image are sent as a new photo message.
   */
  private async renderPage(context: HandlerContext, page: ContentPage): Promise<void> {
    const { locale } = context;
    // Inject configured business values (phone, email, social, …) into the copy.
    const params = page.descriptionParams?.(this.companyConfig.config);
    const title = this.i18n.t(locale, page.titleKey, params);
    const description = this.i18n.t(locale, page.descriptionKey, params);
    // Empty state: never render a blank body — show a friendly placeholder so
    // the page (and its navigation) still works.
    const body =
      description.trim().length > 0 ? description : this.i18n.t(locale, TKey.contentEmptyState);
    const text = `<b>${title}</b>\n\n${body}${this.brandsSection(locale, page)}`;
    const keyboard = buildContentKeyboard(this.i18n.scoped(locale), page);

    if (page.imageUrl) {
      await this.responder.sendPhoto(context, page.imageUrl, text, keyboard);
    } else {
      await this.responder.editText(context, text, keyboard);
    }

    this.logger.log(`${LogEvent.ContentPageRendered}: ${page.id}`, ContentService.name);
  }

  /**
   * Optional "Available brands" section, sourced from the Knowledge Base (brand
   * names only — never duplicated here). Returns '' when the page opts out or no
   * brands exist, so the section never renders empty.
   */
  private brandsSection(locale: HandlerContext['locale'], page: ContentPage): string {
    if (!page.knowledgeBrandsCategory) {
      return '';
    }
    const brands = this.knowledge
      .listArticles(page.knowledgeBrandsCategory)
      .map((article) => article.title);
    if (brands.length === 0) {
      return '';
    }
    return `\n\n<b>${this.i18n.t(locale, TKey.contentSectionBrands)}:</b> ${brands.join(', ')}`;
  }
}
