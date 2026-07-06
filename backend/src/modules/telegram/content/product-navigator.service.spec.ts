import { TelegramUser as PersistedUser } from '@prisma/client';
import { I18nService } from '../../../i18n/i18n.service';
import { TKey } from '../../../i18n/i18n.keys';
import { CallbackData } from '../constants/callback-data.constants';
import { HandlerContext } from '../handlers/handler-context';
import { TelegramResponderService } from '../services/telegram-responder.service';
import { ProductNavigatorService } from './product-navigator.service';
import { contentPageCallback, ContentPageId } from './content.constants';
import * as tree from './product-tree';
import { pnavCallback, ProductNode } from './product-tree';

const user = { id: 'u1', telegramId: BigInt(7), firstName: 'Vasil' } as unknown as PersistedUser;

function ctx(): HandlerContext {
  return {
    chatId: 7,
    user,
    locale: 'uz',
    callbackQuery: {
      id: 'cbq',
      from: { id: 7, is_bot: false, first_name: 'Vasil' },
      message: { message_id: 5, date: 1, chat: { id: 7, type: 'private' } },
    },
  };
}

describe('ProductNavigatorService', () => {
  let responder: { editText: jest.Mock };
  let navigator: ProductNavigatorService;

  beforeEach(() => {
    responder = { editText: jest.fn().mockResolvedValue(undefined) };
    navigator = new ProductNavigatorService(
      responder as unknown as TelegramResponderService,
      new I18nService({ warn: jest.fn() } as never),
      { log: jest.fn() } as never,
    );
  });

  it('ignores non-navigator callbacks', async () => {
    expect(await navigator.handleCallback(ctx(), 'content:page:about')).toBe(false);
    expect(responder.editText).not.toHaveBeenCalled();
  });

  it('renders the Products root: category buttons + Back to the main menu', async () => {
    const handled = await navigator.handleCallback(ctx(), pnavCallback(tree.PRODUCT_ROOT_ID));
    expect(handled).toBe(true);

    const [, , keyboard] = responder.editText.mock.calls[0];
    const buttons = keyboard.inline_keyboard.flat();
    // The Boilers category reuses the existing content page (no page replaced).
    expect(buttons).toContainEqual(
      expect.objectContaining({ callback_data: contentPageCallback(ContentPageId.ProductBoilers) }),
    );
    // Root Back returns to the main menu (root has no Main Menu duplicate).
    expect(buttons).toContainEqual(
      expect.objectContaining({ callback_data: CallbackData.BackToMenu }),
    );
    // 5 categories (<= 6) → no pagination controls.
    expect(buttons).not.toContainEqual(
      expect.objectContaining({ callback_data: pnavCallback(tree.PRODUCT_ROOT_ID, 1) }),
    );
  });

  it('paginates a level with more than 6 children (Next on page 0, Prev on page 1)', async () => {
    const children: ProductNode[] = Array.from({ length: 8 }, (_, i) => ({
      id: `sub_${i}`,
      titleKey: TKey.contentProductsTitle,
      parentId: 'big',
    }));
    const big: ProductNode = {
      id: 'big',
      titleKey: TKey.contentProductsTitle,
      parentId: tree.PRODUCT_ROOT_ID,
      children,
    };
    const spy = jest.spyOn(tree, 'findProductNode').mockImplementation((id) => {
      if (id === 'big') return big;
      return children.find((c) => c.id === id);
    });
    try {
      await navigator.handleCallback(ctx(), pnavCallback('big'));
      let buttons = responder.editText.mock.calls[0][2].inline_keyboard.flat();
      // Page 0 shows a Next control, but not Prev.
      expect(buttons).toContainEqual(
        expect.objectContaining({ callback_data: pnavCallback('big', 1) }),
      );

      await navigator.handleCallback(ctx(), pnavCallback('big', 1));
      buttons = responder.editText.mock.calls[1][2].inline_keyboard.flat();
      // Page 1 shows a Prev control back to page 0.
      expect(buttons).toContainEqual(
        expect.objectContaining({ callback_data: pnavCallback('big', 0) }),
      );
    } finally {
      spy.mockRestore();
    }
  });

  it('renders an action page for a leaf without a content page', async () => {
    const leaf: ProductNode = {
      id: 'gas',
      titleKey: TKey.contentProductBoilersTitle,
      descriptionKey: TKey.contentProductBoilersDescription,
      parentId: 'boilers',
      priceTrigger: CallbackData.Boilers,
      // websiteUrl / catalogUrl intentionally empty (architecture only).
    };
    const spy = jest.spyOn(tree, 'findProductNode').mockReturnValue(leaf);
    try {
      await navigator.handleCallback(ctx(), pnavCallback('gas'));
      const buttons = responder.editText.mock.calls[0][2].inline_keyboard.flat();

      // Request Price reuses the existing flow trigger; Contact Specialist = operator.
      expect(buttons).toContainEqual(
        expect.objectContaining({ callback_data: CallbackData.Boilers }),
      );
      expect(buttons).toContainEqual(
        expect.objectContaining({ callback_data: CallbackData.Operator }),
      );
      // Empty website/catalog URLs → those buttons are omitted (no url buttons).
      expect(buttons.some((b: { url?: string }) => b.url !== undefined)).toBe(false);
      // Back goes up to the parent level; Main Menu jumps home.
      expect(buttons).toContainEqual(
        expect.objectContaining({ callback_data: pnavCallback('boilers') }),
      );
      expect(buttons).toContainEqual(
        expect.objectContaining({ callback_data: CallbackData.BackToMenu }),
      );
    } finally {
      spy.mockRestore();
    }
  });
});
