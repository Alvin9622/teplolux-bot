import { Inject, Injectable, LoggerService, OnModuleInit } from '@nestjs/common';
import { WINSTON_MODULE_NEST_PROVIDER } from 'nest-winston';
import uz from './locales/uz.json';
import ru from './locales/ru.json';
import { DEFAULT_LOCALE, Locale, TranslationKey, Translator } from './i18n.types';

type Catalog = Record<string, unknown>;

/**
 * Translation service.
 *
 * Loads the per-locale catalogs from JSON translation files and resolves dotted
 * keys (e.g. `menu.boilers`) with `{{param}}` interpolation. Unknown keys and
 * missing locales fall back safely to the default locale so the bot never
 * crashes on a translation gap.
 */
@Injectable()
export class I18nService implements OnModuleInit {
  private readonly catalogs: Record<Locale, Catalog> = { uz, ru };

  constructor(@Inject(WINSTON_MODULE_NEST_PROVIDER) private readonly logger: LoggerService) {}

  /** On boot, warn if the locale catalogs have diverging key sets. */
  onModuleInit(): void {
    const uzKeys = this.flatten(this.catalogs.uz).sort();
    const ruKeys = this.flatten(this.catalogs.ru).sort();
    const missingInRu = uzKeys.filter((key) => !ruKeys.includes(key));
    const missingInUz = ruKeys.filter((key) => !uzKeys.includes(key));
    if (missingInRu.length > 0 || missingInUz.length > 0) {
      this.logger.warn(
        `i18n catalog mismatch — missing in ru: [${missingInRu.join(', ')}], missing in uz: [${missingInUz.join(', ')}]`,
        I18nService.name,
      );
    }
  }

  /** Translate a key for a locale, interpolating `{{param}}` placeholders. */
  t(locale: Locale, key: TranslationKey, params?: Record<string, string | number>): string {
    const value =
      this.resolve(this.catalogs[locale], key) ?? this.resolve(this.catalogs[DEFAULT_LOCALE], key);

    if (typeof value !== 'string') {
      this.logger.warn(`Missing translation for key "${key}" (${locale})`, I18nService.name);
      return key;
    }
    return this.interpolate(value, params);
  }

  /** Build a locale-bound {@link Translator} for keyboards and handlers. */
  scoped(locale: Locale): Translator {
    return (key, params) => this.t(locale, key, params);
  }

  /** Resolve a dotted key against a catalog object. */
  private resolve(catalog: Catalog | undefined, key: string): unknown {
    if (!catalog) {
      return undefined;
    }
    return key.split('.').reduce<unknown>((node, segment) => {
      if (node && typeof node === 'object' && segment in (node as Catalog)) {
        return (node as Catalog)[segment];
      }
      return undefined;
    }, catalog);
  }

  /** Replace `{{param}}` tokens with the provided values. */
  private interpolate(template: string, params?: Record<string, string | number>): string {
    if (!params) {
      return template;
    }
    return template.replace(/\{\{\s*(\w+)\s*\}\}/g, (match, name: string) =>
      name in params ? String(params[name]) : match,
    );
  }

  /** Flatten a nested catalog into dotted leaf keys (for parity checks). */
  private flatten(catalog: Catalog, prefix = ''): string[] {
    return Object.entries(catalog).flatMap(([key, value]) => {
      const path = prefix ? `${prefix}.${key}` : key;
      return value && typeof value === 'object' ? this.flatten(value as Catalog, path) : [path];
    });
  }
}
