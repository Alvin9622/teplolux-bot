import { Module } from '@nestjs/common';
import { FaqService } from './faq.service';
import { FAQ_SOURCE, MarkdownFaqSource } from './faq.source';

/**
 * FAQ module.
 *
 * Binds the default Markdown-file source to {@link FAQ_SOURCE} and exports
 * {@link FaqService}. To move the FAQ to a database / CMS later, replace only the
 * `useClass` binding here — no changes to consumers.
 */
@Module({
  providers: [{ provide: FAQ_SOURCE, useClass: MarkdownFaqSource }, FaqService],
  exports: [FaqService],
})
export class FaqModule {}
