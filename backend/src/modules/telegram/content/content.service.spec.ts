import { TelegramUser as PersistedUser } from '@prisma/client';
import { I18nService } from '../../../i18n/i18n.service';
import { TKey } from '../../../i18n/i18n.keys';
import { CallbackData } from '../constants/callback-data.constants';
import { HandlerContext } from '../handlers/handler-context';
import { TelegramResponderService } from '../services/telegram-responder.service';
import { ContentService } from './content.service';
import { ContentRegistry } from './content.registry';
import { ContentAction, ContentPageId, contentPageCallback } from './content.constants';
import { ContentPage } from './content.types';

const user: PersistedUser = {
  id: 'u1',
  telegramId: BigInt(7),
  username: null,
  firstName: 'Vasil',
  lastName: null,
  languageCode: 'uz',
  language: 'UZ',
  phone: null,
  isBlocked: false,
  createdAt: new Date(),
  updatedAt: new Date(),
  lastActivity: new Date(),
};

function ctx(): HandlerContext {
  return {
    chatId: 7,
    user,
    locale: 'uz',
    callbackQuery: {
      id: 'cbq',
      from: { id: 7, is_bot: false, first_name: 'Vasil' },
      message: { message_id: 42, date: 1, chat: { id: 7, type: 'private' } },
    },
  };
}

describe('ContentService', () => {
  let responder: { editText: jest.Mock; sendText: jest.Mock; sendPhoto: jest.Mock };
  let registry: ContentRegistry;
  let service: ContentService;

  beforeEach(() => {
    responder = {
      editText: jest.fn().mockResolvedValue(undefined),
      sendText: jest.fn().mockResolvedValue(undefined),
      sendPhoto: jest.fn().mockResolvedValue(undefined),
    };
    registry = new ContentRegistry();
    service = new ContentService(
      registry,
      responder as unknown as TelegramResponderService,
      new I18nService({ warn: jest.fn() } as never),
      { log: jest.fn() } as never,
    );
  });

  it('renders a known page by editing the message with title + description', async () => {
    const handled = await service.handleCallback(ctx(), contentPageCallback(ContentPageId.About));

    expect(handled).toBe(true);
    expect(responder.editText).toHaveBeenCalledTimes(1);
    const [, text, keyboard] = responder.editText.mock.calls[0];
    expect(text).toContain('Teplolux');
    expect(keyboard.inline_keyboard.length).toBeGreaterThan(0);
  });

  it('builds every supported button type with the right payload', async () => {
    await service.handleCallback(ctx(), contentPageCallback(ContentPageId.Warranty));
    const [, , keyboard] = responder.editText.mock.calls[0];
    const buttons = keyboard.inline_keyboard.flat();

    // page navigation
    expect(buttons).toContainEqual(
      expect.objectContaining({ callback_data: contentPageCallback(ContentPageId.Contacts) }),
    );
    // start conversation flow (reuses the service trigger)
    expect(buttons).toContainEqual(
      expect.objectContaining({ callback_data: CallbackData.Service }),
    );
    // back resolves to the parent page (about)
    expect(buttons).toContainEqual(
      expect.objectContaining({ callback_data: contentPageCallback(ContentPageId.About) }),
    );
    // main menu reuses the existing menu callback
    expect(buttons).toContainEqual(
      expect.objectContaining({ callback_data: CallbackData.BackToMenu }),
    );
  });

  it('renders a website as a url button and a phone as a callback button', async () => {
    await service.handleCallback(ctx(), contentPageCallback(ContentPageId.Contacts));
    const [, , keyboard] = responder.editText.mock.calls[0];
    const buttons = keyboard.inline_keyboard.flat();

    expect(buttons.some((b: { url?: string }) => typeof b.url === 'string')).toBe(true);
    expect(
      buttons.some((b: { callback_data?: string }) =>
        b.callback_data?.startsWith(ContentAction.PhonePrefix),
      ),
    ).toBe(true);
  });

  it('answers a phone button by sending the callable number', async () => {
    const handled = await service.handleCallback(
      ctx(),
      `${ContentAction.PhonePrefix}+998901112233`,
    );

    expect(handled).toBe(true);
    expect(responder.sendText).toHaveBeenCalledTimes(1);
    expect(responder.sendText.mock.calls[0][1]).toContain('+998901112233');
  });

  it('sends a photo (new message) for a page that has an image', async () => {
    const imagePage: ContentPage = {
      id: 'promo',
      titleKey: TKey.contentAboutTitle,
      descriptionKey: TKey.contentAboutDescription,
      imageUrl: 'https://example.com/promo.jpg',
      buttons: [[{ labelKey: TKey.contentButtonMainMenu, action: { type: 'mainMenu' } }]],
    };
    registry.register(imagePage);

    await service.handleCallback(ctx(), contentPageCallback('promo'));

    expect(responder.sendPhoto).toHaveBeenCalledTimes(1);
    expect(responder.editText).not.toHaveBeenCalled();
  });

  it('does not handle unknown pages or non-content callbacks', async () => {
    expect(await service.handleCallback(ctx(), contentPageCallback('does-not-exist'))).toBe(false);
    expect(await service.handleCallback(ctx(), 'menu:something')).toBe(false);
  });
});

describe('ContentRegistry', () => {
  it('ships the four company pages', () => {
    const registry = new ContentRegistry();
    for (const id of Object.values(ContentPageId)) {
      expect(registry.has(id)).toBe(true);
    }
  });
});
