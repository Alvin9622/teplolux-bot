import { TelegramUser as PersistedUser } from '@prisma/client';
import { I18nService } from '../../../i18n/i18n.service';
import { CallbackData } from '../constants/callback-data.constants';
import { contentPageCallback } from '../content/content.constants';
import { HandlerContext } from '../handlers/handler-context';
import { TelegramResponderService } from '../services/telegram-responder.service';
import { FaqPresenterService } from './faq-presenter.service';
import { FaqService } from './faq.service';
import { faqItemCallback, faqListCallback } from './faq.presentation';

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

describe('FaqPresenterService', () => {
  let responder: { editText: jest.Mock };
  let faq: {
    getItem: jest.Mock;
    listItems: jest.Mock;
  };
  let presenter: FaqPresenterService;

  const deliveryItem = {
    id: 'delivery',
    question: 'How does delivery work?',
    answer: 'We deliver across the country.',
    category: 'orders',
    keywords: [],
  };

  beforeEach(() => {
    responder = { editText: jest.fn().mockResolvedValue(undefined) };
    faq = {
      getItem: jest.fn((id: string) => (id === 'delivery' ? deliveryItem : undefined)),
      listItems: jest.fn().mockReturnValue([]),
    };
    presenter = new FaqPresenterService(
      faq as unknown as FaqService,
      responder as unknown as TelegramResponderService,
      new I18nService({ warn: jest.fn() } as never),
      { log: jest.fn() } as never,
    );
  });

  it('ignores non-FAQ callbacks', async () => {
    expect(await presenter.handleCallback(ctx(), 'menu:something')).toBe(false);
    expect(responder.editText).not.toHaveBeenCalled();
  });

  it('renders a product FAQ list with question buttons and a Back to the product page', async () => {
    const handled = await presenter.handleCallback(ctx(), faqListCallback('boilers'));

    expect(handled).toBe(true);
    const [, , keyboard] = responder.editText.mock.calls[0];
    const buttons = keyboard.inline_keyboard.flat();

    // A question button that opens the delivery answer for this scope.
    expect(buttons).toContainEqual(
      expect.objectContaining({ callback_data: faqItemCallback('boilers', 'delivery') }),
    );
    // Back returns to the product page; Main Menu jumps home.
    expect(buttons).toContainEqual(
      expect.objectContaining({ callback_data: contentPageCallback('product_boilers') }),
    );
    expect(buttons).toContainEqual(
      expect.objectContaining({ callback_data: CallbackData.BackToMenu }),
    );
  });

  it('renders a single FAQ answer with Back to the list', async () => {
    await presenter.handleCallback(ctx(), faqItemCallback('boilers', 'delivery'));

    const [, text, keyboard] = responder.editText.mock.calls[0];
    expect(text).toContain(deliveryItem.question);
    expect(text).toContain(deliveryItem.answer);
    const buttons = keyboard.inline_keyboard.flat();
    expect(buttons).toContainEqual(
      expect.objectContaining({ callback_data: faqListCallback('boilers') }),
    );
  });

  it('recovers to the list when the FAQ item is unknown/expired', async () => {
    await presenter.handleCallback(ctx(), faqItemCallback('boilers', 'does-not-exist'));

    // Falls back to rendering the list (a keyboard with the question buttons).
    const [, , keyboard] = responder.editText.mock.calls[0];
    expect(keyboard.inline_keyboard.flat()).toContainEqual(
      expect.objectContaining({ callback_data: faqItemCallback('boilers', 'delivery') }),
    );
  });

  it('shows a friendly empty state for a scope with no items', async () => {
    faq.listItems.mockReturnValue([]);
    await presenter.handleCallback(ctx(), faqListCallback('unknown-category'));

    // Still renders (empty-state text + navigation) — never crashes.
    expect(responder.editText).toHaveBeenCalledTimes(1);
    const [, , keyboard] = responder.editText.mock.calls[0];
    expect(keyboard.inline_keyboard.flat()).toContainEqual(
      expect.objectContaining({ callback_data: CallbackData.BackToMenu }),
    );
  });
});
