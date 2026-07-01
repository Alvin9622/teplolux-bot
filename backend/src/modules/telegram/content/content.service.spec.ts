import { TelegramUser as PersistedUser } from '@prisma/client';
import { I18nService } from '../../../i18n/i18n.service';
import { TKey } from '../../../i18n/i18n.keys';
import { CallbackData } from '../constants/callback-data.constants';
import { HandlerContext } from '../handlers/handler-context';
import { TelegramResponderService } from '../services/telegram-responder.service';
import { ContentService } from './content.service';
import { ContentRegistry } from './content.registry';
import { ContentAction, ContentPageId, contentPageCallback } from './content.constants';
import { CATALOG_URLS, CatalogCategory } from './catalog.config';
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
    // A synthetic page exercising all action types (independent of shipped pages).
    const kitchenSink: ContentPage = {
      id: 'kitchen',
      titleKey: TKey.contentAboutTitle,
      descriptionKey: TKey.contentAboutDescription,
      parentId: ContentPageId.About,
      buttons: [
        [
          {
            labelKey: TKey.contentButtonContacts,
            action: { type: 'page', pageId: ContentPageId.Contacts },
          },
        ],
        [
          {
            labelKey: TKey.contentButtonRequestPrice,
            action: { type: 'flow', trigger: CallbackData.Service },
          },
        ],
        [
          {
            labelKey: TKey.contentButtonWebsite,
            action: { type: 'url', url: 'https://x.example' },
          },
        ],
        [{ labelKey: TKey.contentButtonCall, action: { type: 'phone', phone: '+998900000000' } }],
        [
          {
            labelKey: TKey.contentButtonLocation,
            action: { type: 'callback', data: CallbackData.Location },
          },
        ],
        [{ labelKey: TKey.contentButtonBack, action: { type: 'back' } }],
        [{ labelKey: TKey.contentButtonMainMenu, action: { type: 'mainMenu' } }],
      ],
    };
    registry.register(kitchenSink);

    await service.handleCallback(ctx(), contentPageCallback('kitchen'));
    const [, , keyboard] = responder.editText.mock.calls[0];
    const buttons = keyboard.inline_keyboard.flat();

    // page navigation
    expect(buttons).toContainEqual(
      expect.objectContaining({ callback_data: contentPageCallback(ContentPageId.Contacts) }),
    );
    // start conversation flow (reuses an existing flow trigger)
    expect(buttons).toContainEqual(
      expect.objectContaining({ callback_data: CallbackData.Service }),
    );
    // website -> url button
    expect(buttons).toContainEqual(expect.objectContaining({ url: 'https://x.example' }));
    // phone -> content phone callback
    expect(
      buttons.some((b: { callback_data?: string }) =>
        b.callback_data?.startsWith(ContentAction.PhonePrefix),
      ),
    ).toBe(true);
    // callback passthrough -> reuses the existing Location handler
    expect(buttons).toContainEqual(
      expect.objectContaining({ callback_data: CallbackData.Location }),
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

  it('renders Products as a content page (no lead flow) with category links only', async () => {
    await service.handleCallback(ctx(), contentPageCallback(ContentPageId.Products));
    const [, , keyboard] = responder.editText.mock.calls[0];
    const buttons = keyboard.inline_keyboard.flat();

    // Category buttons open content pages; none of them is a flow trigger.
    expect(buttons).toContainEqual(
      expect.objectContaining({ callback_data: contentPageCallback(ContentPageId.ProductBoilers) }),
    );
    const flowTriggers = [
      CallbackData.Boilers,
      CallbackData.Radiators,
      CallbackData.FloorHeating,
      CallbackData.WaterHeaters,
      CallbackData.Pumps,
    ];
    for (const b of buttons) {
      expect(flowTriggers).not.toContain(b.callback_data);
    }
  });

  it('exposes Request Price (lead flow trigger) on a product category page', async () => {
    await service.handleCallback(ctx(), contentPageCallback(ContentPageId.ProductBoilers));
    const [, , keyboard] = responder.editText.mock.calls[0];
    const buttons = keyboard.inline_keyboard.flat();

    // Request Price carries the existing product flow trigger.
    expect(buttons).toContainEqual(
      expect.objectContaining({ callback_data: CallbackData.Boilers }),
    );
    // View Catalog is a url button pointing at the configured per-category catalog.
    expect(buttons).toContainEqual(
      expect.objectContaining({ url: CATALOG_URLS[CatalogCategory.Boilers] }),
    );
    // Back returns to the Products page.
    expect(buttons).toContainEqual(
      expect.objectContaining({ callback_data: contentPageCallback(ContentPageId.Products) }),
    );
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
  it('ships every declared content page (about, contacts, products, categories, ...)', () => {
    const registry = new ContentRegistry();
    for (const id of Object.values(ContentPageId)) {
      expect(registry.has(id)).toBe(true);
    }
  });
});
