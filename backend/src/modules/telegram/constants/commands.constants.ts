/**
 * Supported bot commands. Each value is the command keyword without its leading
 * slash. Handlers register themselves against these constants so adding a new
 * command is a single, localised change.
 */
export const BotCommand = {
  Start: 'start',
  Help: 'help',
  Catalog: 'catalog',
  Service: 'service',
  Dealer: 'dealer',
  Operator: 'operator',
  Contact: 'contact',
  Location: 'location',
  Cancel: 'cancel',
} as const;

export type BotCommandName = (typeof BotCommand)[keyof typeof BotCommand];

/** Commands advertised to Telegram (shown in the client's command menu). */
export const BOT_COMMAND_DESCRIPTIONS: ReadonlyArray<{
  command: BotCommandName;
  description: string;
}> = [
  { command: BotCommand.Start, description: 'Start / restart the assistant' },
  { command: BotCommand.Catalog, description: 'Browse the product catalog' },
  { command: BotCommand.Service, description: 'Request technical service' },
  { command: BotCommand.Dealer, description: 'Become a dealer' },
  { command: BotCommand.Operator, description: 'Talk to an operator' },
  { command: BotCommand.Contact, description: 'Contact information' },
  { command: BotCommand.Location, description: 'Our location' },
  { command: BotCommand.Cancel, description: 'Cancel the current request' },
  { command: BotCommand.Help, description: 'How to use the assistant' },
];
