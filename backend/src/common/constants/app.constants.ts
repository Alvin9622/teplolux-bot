import { readFileSync } from 'node:fs';
import { join } from 'node:path';

/**
 * Resolve the application version from `package.json` once at module load.
 *
 * Reading from disk (rather than importing the JSON) keeps the compiled output
 * tree clean and avoids `rootDir` issues. Falls back gracefully if the file is
 * unavailable (e.g. unusual runtime layout).
 */
function resolveAppVersion(): string {
  try {
    const pkgPath = join(process.cwd(), 'package.json');
    const pkg = JSON.parse(readFileSync(pkgPath, 'utf-8')) as { version?: string };
    return pkg.version ?? '0.0.0';
  } catch {
    return '0.0.0';
  }
}

/** Current application version (from package.json). */
export const APP_VERSION: string = resolveAppVersion();

/** Human-readable application name used in docs and bot messaging. */
export const APP_NAME = 'Teplolux AI CRM Assistant';
