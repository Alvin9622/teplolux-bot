import { APP_NAME } from '../../../common/constants/app.constants';

/**
 * User-facing bot copy.
 *
 * Centralising message text keeps presentation out of the handlers, satisfies
 * the "no hardcoded strings" rule, and provides a single seam for the future
 * multi-language module to plug into.
 */
export const BotMessage = {
  welcome: (firstName?: string): string =>
    [
      `👋 <b>Welcome${firstName ? `, ${escapeHtml(firstName)}` : ''}!</b>`,
      '',
      `This is the <b>${APP_NAME}</b> — your single point of contact with Teplolux.`,
      '',
      'Choose a section from the menu below:',
    ].join('\n'),

  help: [
    '<b>How can I help you?</b>',
    '',
    'Available commands:',
    '/start — open the main menu',
    '/catalog — browse our products',
    '/service — request technical service',
    '/dealer — become a dealer',
    '/operator — talk to a human operator',
    '/contact — contact information',
    '/location — our location',
    '/help — show this message',
  ].join('\n'),

  catalogIntro: '<b>🛍 Product catalog</b>\n\nSelect a product category to learn more:',

  category: {
    boilers:
      '<b>🏠 Boilers</b>\n\nReliable heating boilers for homes and businesses. ' +
      'Our specialists will help you choose the right capacity and model.',
    radiators:
      '<b>🔥 Radiators</b>\n\nHigh-efficiency radiators in a wide range of sizes and finishes.',
    floorHeating:
      '<b>♨️ Floor Heating</b>\n\nComfortable underfloor heating systems for any space.',
  },

  service:
    '<b>🛠 Service request</b>\n\nDescribe the issue and our technical team will get back to you. ' +
    'You can also share your phone number so an operator can call you.',

  dealer:
    '<b>🤝 Become a dealer</b>\n\nPartner with Teplolux and grow your business. ' +
    'Leave your contact details and our partnership team will reach out.',

  operator:
    '<b>👨 Contact operator</b>\n\nYou have been queued for a human operator. ' +
    'Please describe your question and we will respond shortly.',

  contact: [
    '<b>📞 Contact information</b>',
    '',
    'Phone: +998 (00) 000-00-00',
    'Email: info@teplolux.example.com',
    'Working hours: Mon–Sat, 09:00–18:00',
  ].join('\n'),

  location: '<b>📍 Our location</b>\n\nWe have shared our address on the map below.',

  unknownCommand: 'Sorry, I did not recognise that command. Use /help to see what I can do.',

  fallback: 'I received your message. Use the menu or /help to get started.',

  callbackAcknowledged: 'Done',
} as const;

/** Minimal HTML escaping for user-provided values interpolated into HTML messages. */
export function escapeHtml(value: string): string {
  return value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
