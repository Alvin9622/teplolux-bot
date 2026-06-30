import { Language } from '@prisma/client';
import ru from './locales/ru.json';

/**
 * Supported interface locales. English is intentionally NOT included yet.
 * The structure of {@link ru} (and {@link uz}) is the single source of truth
 * for the available translation keys.
 */
export type Locale = 'uz' | 'ru';

export const SUPPORTED_LOCALES: readonly Locale[] = ['uz', 'ru'];

/** Locale used as a safe fallback before the user has chosen one. */
export const DEFAULT_LOCALE: Locale = 'uz';

/** Recursively derive the dotted key paths (e.g. `menu.boilers`) of a catalog. */
type DottedKeys<T, Prefix extends string = ''> = {
  [K in keyof T & string]: T[K] extends string
    ? `${Prefix}${K}`
    : DottedKeys<T[K], `${Prefix}${K}.`>;
}[keyof T & string];

/** Every valid leaf translation key, derived from the locale catalog shape. */
export type TranslationKey = DottedKeys<typeof ru>;

/** A locale-bound translation function handed to keyboards and handlers. */
export type Translator = (key: TranslationKey, params?: Record<string, string | number>) => string;

/** Narrowing guard for raw strings coming from the database / Telegram. */
export function isLocale(value: string | null | undefined): value is Locale {
  return value === 'uz' || value === 'ru';
}

/** Map an application {@link Locale} to the persisted Prisma {@link Language}. */
export function localeToPrismaLanguage(locale: Locale): Language {
  return locale === 'ru' ? Language.RU : Language.UZ;
}

/** Map a persisted Prisma {@link Language} back to a {@link Locale} (null if unset). */
export function prismaLanguageToLocale(language: Language | null | undefined): Locale | null {
  if (language === Language.RU) {
    return 'ru';
  }
  if (language === Language.UZ) {
    return 'uz';
  }
  return null;
}
