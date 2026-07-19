from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

CATEGORIES = ["SEO", "Kontent", "Reklama", "SMM", "CMS", "Boshqa"]


def time_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="▶️ Ishni boshlash", callback_data="tm:track_start")
    kb.button(text="🍅 Pomodoro", callback_data="tm:pomo")
    kb.button(text="📋 Kunlik reja", callback_data="tm:plan")
    kb.button(text="📊 Statistikam", callback_data="tm:stats")
    kb.button(text="🔥 Streak", callback_data="tm:streak")
    kb.button(text="⬅️ Bosh menyu", callback_data="go:main")
    kb.adjust(1, 2, 2, 1)
    return kb.as_markup()


def category_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for cat in CATEGORIES:
        kb.button(text=cat, callback_data=f"tm:cat:{cat}")
    kb.button(text="⬅️ Orqaga", callback_data="tm:menu")
    kb.adjust(2)
    return kb.as_markup()


def active_track_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⏹ Tugatish", callback_data="tm:track_stop")
    kb.adjust(1)
    return kb.as_markup()


def pomo_duration_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🍅 25 daqiqa", callback_data="tm:pomo_dur:25")
    kb.button(text="🍅 50 daqiqa", callback_data="tm:pomo_dur:50")
    kb.button(text="✏️ Boshqa", callback_data="tm:pomo_dur:custom")
    kb.button(text="⬅️ Orqaga", callback_data="tm:menu")
    kb.adjust(2, 1, 1)
    return kb.as_markup()


def active_pomo_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⏹ To'xtatish", callback_data="tm:pomo_cancel")
    kb.adjust(1)
    return kb.as_markup()


def pomodoro_done_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🍅 Yana bir pomodoro", callback_data="tm:pomo")
    kb.button(text="✅ Tugatdim", callback_data="tm:menu")
    kb.adjust(1)
    return kb.as_markup()


def plan_items_kb(items) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for it in items:
        mark = "✅" if it["is_done"] else "⬜️"
        kb.button(text=f"{mark} {it['text'][:30]}",
                  callback_data=f"tm:toggle:{it['id']}")
    kb.button(text="➕ Yangi reja tuzish", callback_data="tm:plan_new")
    kb.button(text="⬅️ Orqaga", callback_data="tm:menu")
    kb.adjust(1)
    return kb.as_markup()
