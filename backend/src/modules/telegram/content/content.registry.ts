import { Injectable } from '@nestjs/common';
import { companyPages } from './pages/company.pages';
import { ContentPage } from './content.types';

/**
 * Registry of content pages.
 *
 * Pages are plain data; the {@link ContentService} resolves them by id here, so
 * adding a page is just registering another {@link ContentPage} — no code
 * changes to the renderer. (This is a static registry, not a CMS.)
 */
@Injectable()
export class ContentRegistry {
  private readonly pages = new Map<string, ContentPage>();

  constructor() {
    companyPages.forEach((page) => this.register(page));
  }

  register(page: ContentPage): void {
    this.pages.set(page.id, page);
  }

  get(id: string): ContentPage | undefined {
    return this.pages.get(id);
  }

  has(id: string): boolean {
    return this.pages.has(id);
  }
}
