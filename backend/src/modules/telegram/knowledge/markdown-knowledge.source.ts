import { readdirSync, readFileSync } from 'node:fs';
import { join, relative } from 'node:path';
import { Inject, Injectable, LoggerService } from '@nestjs/common';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import { GENERAL_CATEGORY, KnowledgeArticle } from './knowledge.types';

/** DI token for the swappable {@link KnowledgeSource}. */
export const KNOWLEDGE_SOURCE = Symbol('KNOWLEDGE_SOURCE');

/**
 * A source of knowledge-base articles.
 *
 * Kept behind an interface so the Markdown-file source used today can later be
 * replaced by a database, CMS or AI/vector-backed source WITHOUT changing the
 * {@link KnowledgeService} or any handler that consumes it.
 */
export interface KnowledgeSource {
  load(): KnowledgeArticle[];
}

const MARKDOWN_EXTENSION = '.md';

/**
 * Loads articles from structured Markdown files under `./articles`.
 *
 * Supports an optional YAML-style front-matter block (`title`, `tags`) and
 * derives sensible defaults (first heading / filename) when it is absent. No
 * external Markdown/YAML dependency, no AI — just the filesystem.
 */
@Injectable()
export class MarkdownKnowledgeSource implements KnowledgeSource {
  private readonly baseDir = join(__dirname, 'articles');

  constructor(@Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService) {}

  load(): KnowledgeArticle[] {
    const files = this.collectMarkdownFiles(this.baseDir);
    const articles: KnowledgeArticle[] = [];

    for (const file of files) {
      try {
        articles.push(this.parseFile(file));
      } catch (error) {
        this.logger.warn(
          `Failed to load knowledge article "${file}": ${
            error instanceof Error ? error.message : String(error)
          }`,
          MarkdownKnowledgeSource.name,
        );
      }
    }

    return articles.sort((a, b) => a.slug.localeCompare(b.slug));
  }

  /** Recursively collect `.md` file paths under a directory (tolerant of a missing dir). */
  private collectMarkdownFiles(dir: string): string[] {
    let entries;
    try {
      entries = readdirSync(dir, { withFileTypes: true });
    } catch {
      this.logger.warn(`Knowledge base directory not found: ${dir}`, MarkdownKnowledgeSource.name);
      return [];
    }

    return entries.flatMap((entry) => {
      const fullPath = join(dir, entry.name);
      if (entry.isDirectory()) {
        return this.collectMarkdownFiles(fullPath);
      }
      return entry.isFile() && entry.name.endsWith(MARKDOWN_EXTENSION) ? [fullPath] : [];
    });
  }

  private parseFile(filePath: string): KnowledgeArticle {
    const raw = readFileSync(filePath, 'utf-8');
    const slug = relative(this.baseDir, filePath)
      .replace(new RegExp(`\\${MARKDOWN_EXTENSION}$`), '')
      .split(/[\\/]/)
      .join('/');
    const category = slug.includes('/') ? slug.split('/')[0] : GENERAL_CATEGORY;

    const { meta, body } = this.splitFrontMatter(raw);
    const title = meta.title ?? this.firstHeading(body) ?? slug.split('/').pop() ?? slug;
    const tags = (meta.tags ?? '')
      .split(',')
      .map((tag) => tag.trim().toLowerCase())
      .filter((tag) => tag.length > 0);

    return { slug, category, title, tags, content: body.trim() };
  }

  /** Parse a leading `---` front-matter block into simple `key: value` pairs. */
  private splitFrontMatter(raw: string): { meta: Record<string, string>; body: string } {
    const normalized = raw.replace(/\r\n/g, '\n');
    if (!normalized.startsWith('---\n')) {
      return { meta: {}, body: normalized };
    }
    const end = normalized.indexOf('\n---', 4);
    if (end === -1) {
      return { meta: {}, body: normalized };
    }

    const block = normalized.slice(4, end);
    const body = normalized.slice(end + 4).replace(/^\n/, '');
    const meta: Record<string, string> = {};
    for (const line of block.split('\n')) {
      const separator = line.indexOf(':');
      if (separator > 0) {
        meta[line.slice(0, separator).trim().toLowerCase()] = line.slice(separator + 1).trim();
      }
    }
    return { meta, body };
  }

  private firstHeading(body: string): string | undefined {
    const match = body.match(/^#\s+(.+)$/m);
    return match ? match[1].trim() : undefined;
  }
}
