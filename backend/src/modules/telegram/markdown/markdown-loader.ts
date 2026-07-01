import { readdirSync, readFileSync } from 'node:fs';
import { join, relative } from 'node:path';

/**
 * A raw Markdown document parsed from disk.
 *
 * Reusable, framework-agnostic building block for any Markdown-backed content
 * (FAQ, and available for future modules) — front-matter is parsed generically
 * and callers map `meta` / `body` into their own domain model.
 */
export interface RawMarkdownDoc {
  /** Path relative to the base dir, without extension, forward-slashed. */
  readonly slug: string;
  /** First folder segment (`''` for a root file). */
  readonly folderCategory: string;
  /** Parsed `key: value` front-matter (keys lower-cased). */
  readonly meta: Record<string, string>;
  /** Markdown body with the front-matter block removed. */
  readonly body: string;
}

/** Minimal logger surface so the loader stays decoupled from any framework. */
export interface MarkdownLoaderLogger {
  warn(message: string, context?: string): void;
}

const MARKDOWN_EXTENSION = '.md';

/** Split a comma-separated front-matter list into trimmed, lower-cased tokens. */
export function parseCsvList(value: string | undefined): string[] {
  return (value ?? '')
    .split(',')
    .map((entry) => entry.trim().toLowerCase())
    .filter((entry) => entry.length > 0);
}

/** Return the text of the first `# Heading` in a Markdown body, if any. */
export function markdownFirstHeading(body: string): string | undefined {
  const match = body.match(/^#\s+(.+)$/m);
  return match ? match[1].trim() : undefined;
}

/**
 * Recursively load and parse all `.md` files under `baseDir`. Tolerant of a
 * missing directory (logs and returns `[]`) and of individual unreadable files.
 */
export function loadMarkdownDocs(baseDir: string, logger?: MarkdownLoaderLogger): RawMarkdownDoc[] {
  const docs: RawMarkdownDoc[] = [];

  for (const filePath of collectMarkdownFiles(baseDir, logger)) {
    try {
      docs.push(parseFile(baseDir, filePath));
    } catch (error) {
      logger?.warn(
        `Failed to load Markdown file "${filePath}": ${
          error instanceof Error ? error.message : String(error)
        }`,
        'MarkdownLoader',
      );
    }
  }

  return docs.sort((a, b) => a.slug.localeCompare(b.slug));
}

function collectMarkdownFiles(dir: string, logger?: MarkdownLoaderLogger): string[] {
  let entries;
  try {
    entries = readdirSync(dir, { withFileTypes: true });
  } catch {
    logger?.warn(`Markdown directory not found: ${dir}`, 'MarkdownLoader');
    return [];
  }

  return entries.flatMap((entry) => {
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      return collectMarkdownFiles(fullPath, logger);
    }
    return entry.isFile() && entry.name.endsWith(MARKDOWN_EXTENSION) ? [fullPath] : [];
  });
}

function parseFile(baseDir: string, filePath: string): RawMarkdownDoc {
  const raw = readFileSync(filePath, 'utf-8');
  const slug = relative(baseDir, filePath)
    .replace(new RegExp(`\\${MARKDOWN_EXTENSION}$`), '')
    .split(/[\\/]/)
    .join('/');
  const folderCategory = slug.includes('/') ? slug.split('/')[0] : '';
  const { meta, body } = splitFrontMatter(raw);
  return { slug, folderCategory, meta, body };
}

/** Parse a leading `---` front-matter block into simple `key: value` pairs. */
function splitFrontMatter(raw: string): { meta: Record<string, string>; body: string } {
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
