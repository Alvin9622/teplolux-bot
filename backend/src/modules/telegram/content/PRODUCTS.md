# Product Navigator — configuration guide

The Product Navigator (Products → Category → Subcategory → Actions) is fully
**data-driven**. All product structure lives in **one file**:

```
src/modules/telegram/content/products.config.ts   →  PRODUCTS_CONFIG
```

> You never edit `ProductNavigatorService` or `product-tree.ts` to add, hide or
> re-order products. Change only `products.config.ts`. The navigator loads the
> tree from the config at startup (`buildProductTree`) and renders it as-is.

## Node fields

| Field            | Required | Meaning                                                        |
| ---------------- | -------- | ------------------------------------------------------------- |
| `id`             | yes      | Unique id used in callbacks. No `:` characters.               |
| `title_uz`       | yes      | Uzbek title (shown on the button / page).                     |
| `title_ru`       | yes      | Russian title.                                                |
| `description_uz` | no       | Uzbek description (shown on a level / action page).           |
| `description_ru` | no       | Russian description.                                          |
| `icon`           | no       | Emoji prefixed to the title (e.g. `🔥`).                       |
| `websiteUrl`     | no       | "🌐 View Products" link. Leave `''` until a real URL exists. |
| `catalogUrl`     | no       | "📖 Catalog" link.                                             |
| `parentId`       | no       | Normally derived from nesting; set only to override.          |
| `children`       | no       | Sub-nodes. Presence ⇒ this node opens the next level.         |
| `isVisible`      | no       | `false` hides the node (kept in config). Defaults to visible. |
| `sortOrder`      | no       | Ascending order within a level. Defaults to `0`.              |
| `contentPageId`  | no       | Leaf: open an existing content page instead of an action page.|
| `priceTrigger`   | no       | Leaf action page: reuse an existing Request Price flow.       |

## How to add a category

Add an object to `PRODUCTS_CONFIG.children`:

```ts
{
  id: 'air_conditioners',
  icon: '❄️',
  title_uz: 'Konditsionerlar',
  title_ru: 'Кондиционеры',
  sortOrder: 60,
  websiteUrl: '',            // fill in later
  catalogUrl: '',            // optional
}
```

A category with **no `children`** and **no `contentPageId`** automatically shows
an **Action Page** (Website / Catalog / Request Price / Contact Specialist /
Back / Main Menu). Set `priceTrigger` to reuse an existing Request Price flow.

## How to add a subcategory

Give a category a `children` array. It then becomes an intermediate level and
opening it shows its sub-nodes (with automatic pagination at 6 per page):

```ts
{
  id: 'boilers',
  icon: '🔥',
  title_uz: 'Kotyollar',
  title_ru: 'Котлы',
  children: [
    { id: 'boilers_gas',      title_uz: 'Gaz',   title_ru: 'Газовые',       sortOrder: 10 },
    { id: 'boilers_electric', title_uz: 'Elektr', title_ru: 'Электрические', sortOrder: 20 },
  ],
}
```

Nesting can go any number of levels deep — the navigator adapts automatically.

## How to attach a website URL

Set `websiteUrl` on the node:

```ts
{ id: 'boilers_gas', title_uz: 'Gaz', title_ru: 'Газовые', websiteUrl: 'https://teplolux.uz/gas' }
```

An empty (`''`) or missing `websiteUrl` simply omits the "🌐 View Products"
button — nothing breaks. Do not invent URLs.

## How to attach a catalog URL

Set `catalogUrl` the same way (optional). An empty/missing value omits the
"📖 Catalog" button.

## Hiding / re-ordering

- `isVisible: false` hides a node without deleting it.
- `sortOrder` controls the order within a level (ascending).

## Future: syncing with teplolux.uz

`PRODUCTS_CONFIG` is plain data, so a future sync can generate it from
teplolux.uz (or load a JSON/DB source) and pass it to `buildProductTree(...)` —
no change to `ProductNavigatorService`, callbacks, navigation or tests.
