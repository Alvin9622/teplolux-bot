import { TKey } from '../../../i18n/i18n.keys';
import { Translator } from '../../../i18n/i18n.types';
import { CallbackData } from '../constants/callback-data.constants';
import { buildNavigationRows } from './content.navigation';
import { contentPageCallback, ContentPageId } from './content.constants';
import { ContentPage } from './content.types';

// Identity-ish translator: labels are irrelevant here, we assert callback_data.
const t = (() => 'label') as unknown as Translator;

function page(partial: Partial<ContentPage>): ContentPage {
  return {
    id: 'x',
    titleKey: TKey.contentAboutTitle,
    descriptionKey: TKey.contentAboutDescription,
    buttons: [],
    ...partial,
  };
}

type Btn = { callback_data?: string };

describe('content navigation footer', () => {
  it('root page: Operator + Back(→ main menu), and NO separate Main Menu button', () => {
    const flat = buildNavigationRows(t, page({ id: 'about' })).flat() as Btn[];

    // Operator reuses the single shared flow trigger (no duplicated handler).
    expect(flat).toContainEqual(expect.objectContaining({ callback_data: CallbackData.Operator }));
    // Back on a root page returns to the main menu.
    expect(flat).toContainEqual(
      expect.objectContaining({ callback_data: CallbackData.BackToMenu }),
    );
    // No duplicate: exactly one button targets the main menu.
    expect(flat.filter((b) => b.callback_data === CallbackData.BackToMenu)).toHaveLength(1);
  });

  it('nested page: Back(→ parent) + Main Menu(→ main menu) + Operator', () => {
    const flat = buildNavigationRows(
      t,
      page({ id: 'product_boilers', parentId: ContentPageId.Products }),
    ).flat() as Btn[];

    // Back returns to the parent page.
    expect(flat).toContainEqual(
      expect.objectContaining({ callback_data: contentPageCallback(ContentPageId.Products) }),
    );
    // A direct Main Menu jump is offered on nested pages.
    expect(flat).toContainEqual(
      expect.objectContaining({ callback_data: CallbackData.BackToMenu }),
    );
    expect(flat).toContainEqual(expect.objectContaining({ callback_data: CallbackData.Operator }));
  });

  it('honours per-page opt-outs and never emits an empty row', () => {
    const rows = buildNavigationRows(
      t,
      page({ nav: { back: false, mainMenu: false, operator: false } }),
    );
    expect(rows).toHaveLength(0);
  });
});
