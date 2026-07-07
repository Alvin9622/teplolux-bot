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

/**
 * Commands advertised to Telegram (shown in the client's command menu).
 *
 * Customer-facing: descriptions are published in Uzbek (default, primary
 * market) and Russian via `setMyCommands` language codes — never in English.
 */
export const BOT_COMMAND_DESCRIPTIONS: ReadonlyArray<{
  command: BotCommandName;
  /** Uzbek description — also the default for unrecognised client languages. */
  description: string;
  /** Russian description, published with language_code "ru". */
  descriptionRu: string;
}> = [
  {
    command: BotCommand.Start,
    description: 'Botni ishga tushirish / asosiy menyu',
    descriptionRu: 'Запустить бота / главное меню',
  },
  {
    command: BotCommand.Catalog,
    description: 'Mahsulotlar katalogi',
    descriptionRu: 'Каталог продукции',
  },
  {
    command: BotCommand.Service,
    description: "Servis so'rovi",
    descriptionRu: 'Заявка на сервис',
  },
  { command: BotCommand.Dealer, description: "Diler bo'lish", descriptionRu: 'Стать дилером' },
  {
    command: BotCommand.Operator,
    description: "Operator bilan bog'lanish",
    descriptionRu: 'Связаться с оператором',
  },
  {
    command: BotCommand.Contact,
    description: "Aloqa ma'lumotlari",
    descriptionRu: 'Контактная информация',
  },
  { command: BotCommand.Location, description: 'Bizning manzil', descriptionRu: 'Наш адрес' },
  {
    command: BotCommand.Cancel,
    description: "Joriy so'rovni bekor qilish",
    descriptionRu: 'Отменить текущую заявку',
  },
  {
    command: BotCommand.Help,
    description: "Botdan foydalanish bo'yicha yordam",
    descriptionRu: 'Помощь по использованию бота',
  },
];
