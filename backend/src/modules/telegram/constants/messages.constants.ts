/**
 * Presentation helpers for Telegram messages.
 *
 * All user-facing copy now lives in the i18n translation files
 * (`src/i18n/locales/*.json`); this module only retains framework-agnostic
 * formatting utilities shared by handlers.
 */

/** Minimal HTML escaping for user-provided values interpolated into HTML messages. */
export function escapeHtml(value: string): string {
  return value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
