import { Module } from '@nestjs/common';
import { KnowledgeService } from './knowledge.service';
import { KNOWLEDGE_SOURCE, MarkdownKnowledgeSource } from './markdown-knowledge.source';

/**
 * Knowledge base module.
 *
 * Binds the default Markdown-file source to {@link KNOWLEDGE_SOURCE} and exports
 * {@link KnowledgeService}. To move the knowledge base to a database / CMS or an
 * AI/vector-backed source later, replace only the `useClass` binding here — no
 * changes to the Telegram handlers that consume the service.
 */
@Module({
  providers: [{ provide: KNOWLEDGE_SOURCE, useClass: MarkdownKnowledgeSource }, KnowledgeService],
  exports: [KnowledgeService],
})
export class KnowledgeModule {}
