"""
G'oyalar va takliflar bo'limi.
Barcha foydalanuvchilar (admin + employee) g'oya/muammo/kelajak rejasi yoza oladi.
Admin g'oyalarni ko'radi, status o'zgartiradi, izoh qoldiradi.
Google Sheets ga avtomatik sinxronlanadi.
"""
import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

import database as db
from config import ADMIN_IDS
from keyboards.kb import ideas_menu_kb, idea_view_kb, ideas_list_kb, back_kb
from texts import T

logger = logging.getLogger(__name__)
router = Router()

TYPE_LABELS = {
    "idea":    {"uz": "💡 G'oya", "ru": "💡 Идея"},
    "problem": {"uz": "⚠️ Muammo", "ru": "⚠️ Проблема"},
    "future":  {"uz": "🚀 Kelajak", "ru": "🚀 План"},
}
STATUS_LABELS = {
    "new":      {"uz": "🆕 Yangi",             "ru": "🆕 Новая"},
    "review":   {"uz": "👀 Ko'rib chiqilmoqda", "ru": "👀 На рассмотрении"},
    "accepted": {"uz": "✅ Qabul qilindi",      "ru": "✅ Принята"},
    "rejected": {"uz": "❌ Rad etildi",         "ru": "❌ Отклонена"},
}


class IdeaStates(StatesGroup):
    waiting_text = State()
    waiting_admin_note = State()


def _type_label(idea_type, lang):
    return TYPE_LABELS.get(idea_type, {}).get(lang, idea_type)

def _status_label(status, lang):
    return STATUS_LABELS.get(status, {}).get(lang, status)

def _idea_text(idea, lang):
    tip    = _type_label(idea.get("type"), lang)
    status = _status_label(idea.get("status"), lang)
    uname  = f"@{idea['username']}" if idea.get("username") else ""
    note   = f"\n\n📝 <b>Admin izohi:</b> {idea['admin_note']}" if idea.get("admin_note") else ""
    date   = (idea.get("created_at") or "")[:16].replace("T", " ")
    return (
        f"💡 <b>G'oya #{idea['id']}</b>\n"
        f"📌 Tur: {tip}\n"
        f"📊 Holat: {status}\n"
        f"👤 {idea.get('full_name') or '?'} {uname}\n"
        f"🕐 {date}\n\n"
        f"{idea.get('text') or ''}"
        f"{note}"
    )


# ─── MENU ────────────────────────────────────────────────────────

@router.callback_query(F.data == "go:ideas")
async def ideas_menu(cb: CallbackQuery, state: FSMContext = None):
    if state:
        await state.clear()
    user = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer("Avval /start bosing", show_alert=True)
        return
    lang     = user.get("lang", "uz")
    is_admin = user["role"] == "admin"
    await cb.message.edit_text(
        T(lang, "ideas_menu_title"),
        reply_markup=ideas_menu_kb(lang, is_admin=is_admin),
        parse_mode="HTML",
    )
    await cb.answer()


# ─── ADD IDEA ────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("idea:add:"))
async def idea_add_start(cb: CallbackQuery, state: FSMContext):
    user = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(); return
    lang      = user.get("lang", "uz")
    idea_type = cb.data.split(":")[2]  # idea / problem / future
    await state.set_state(IdeaStates.waiting_text)
    await state.update_data(idea_type=idea_type, lang=lang)
    tip_label = _type_label(idea_type, lang)
    cancel_text = "❌ Bekor qilish" if lang == "uz" else "❌ Отменить"
    await cb.message.edit_text(
        f"<b>{tip_label}</b>\n\n{T(lang, 'ideas_ask_text')}",
        parse_mode="HTML",
        reply_markup=back_kb(lang, "ideas"),
    )
    await cb.answer()


@router.message(IdeaStates.waiting_text)
async def idea_save(message: Message, state: FSMContext):
    data       = await state.get_data()
    lang       = data.get("lang", "uz")
    idea_type  = data.get("idea_type", "idea")
    user       = await db.get_user(message.from_user.id)
    if not user:
        await state.clear(); return

    idea_id = await db.create_idea(
        tg_id     = message.from_user.id,
        full_name = user["full_name"],
        username  = message.from_user.username or "",
        role      = user["role"],
        idea_type = idea_type,
        text      = message.text.strip(),
    )
    await state.clear()
    await message.answer(T(lang, "ideas_saved"), parse_mode="HTML",
                         reply_markup=ideas_menu_kb(lang, is_admin=(user["role"] == "admin")))

    # Google Sheets sync
    try:
        idea = await db.get_idea(idea_id)
        from utils.sheets import sync_idea
        await sync_idea(idea)
    except Exception as e:
        logger.warning("sync_idea error: %s", e)

    # Admin bildirishnomasi
    tip_label = _type_label(idea_type, lang)
    uname     = f"@{message.from_user.username}" if message.from_user.username else ""
    notify    = (
        f"💡 <b>Yangi g'oya/taklif!</b>\n"
        f"👤 {user['full_name']} {uname}\n"
        f"📌 Tur: {tip_label}\n\n"
        f"{message.text.strip()[:300]}\n\n"
        f"<i>Ko'rish: /start → G'oyalar #{idea_id}</i>"
    )
    for aid in ADMIN_IDS:
        if aid != message.from_user.id:
            try:
                await message.bot.send_message(aid, notify, parse_mode="HTML")
            except Exception:
                pass


# ─── LIST ────────────────────────────────────────────────────────

@router.callback_query(F.data.in_({"idea:list", "idea:filter:new"}))
async def idea_list(cb: CallbackQuery):
    user = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(); return
    lang     = user.get("lang", "uz")
    is_admin = user["role"] == "admin"
    flt      = "new" if cb.data == "idea:filter:new" else None

    if is_admin:
        ideas = await db.get_ideas(status=flt)
        title = T(lang, "ideas_list_title")
    else:
        ideas = await db.get_ideas(tg_id=cb.from_user.id)
        title = T(lang, "ideas_my_title")

    if not ideas:
        await cb.message.edit_text(
            f"{title}\n\n{T(lang, 'ideas_empty')}",
            reply_markup=back_kb(lang, "ideas"),
            parse_mode="HTML",
        )
        await cb.answer(); return

    counts = {"new": 0, "review": 0, "accepted": 0, "rejected": 0}
    for idea in ideas:
        s = idea.get("status", "new")
        if s in counts:
            counts[s] += 1

    summary = (
        f"🆕 {counts['new']}  👀 {counts['review']}  "
        f"✅ {counts['accepted']}  ❌ {counts['rejected']}"
    )
    await cb.message.edit_text(
        f"{title}\n{summary}",
        reply_markup=ideas_list_kb(lang, ideas, flt or "all"),
        parse_mode="HTML",
    )
    await cb.answer()


# ─── VIEW ────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("idea:view:"))
async def idea_view(cb: CallbackQuery):
    idea_id = int(cb.data.split(":")[2])
    user    = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(); return
    lang     = user.get("lang", "uz")
    is_admin = user["role"] == "admin"
    idea     = await db.get_idea(idea_id)
    if not idea:
        await cb.answer("Topilmadi", show_alert=True); return

    # Faqat o'z g'oyasini yoki admin ko'rishi mumkin
    if not is_admin and idea["tg_id"] != cb.from_user.id:
        await cb.answer("Ruxsat yo'q", show_alert=True); return

    await cb.message.edit_text(
        _idea_text(idea, lang),
        reply_markup=idea_view_kb(lang, idea_id, idea["status"], is_admin=is_admin),
        parse_mode="HTML",
    )
    await cb.answer()


# ─── ADMIN: STATUS ───────────────────────────────────────────────

@router.callback_query(F.data.startswith("idea:status:"))
async def idea_set_status(cb: CallbackQuery):
    parts   = cb.data.split(":")
    idea_id = int(parts[2])
    status  = parts[3]
    user    = await db.get_user(cb.from_user.id)
    if not user or user["role"] != "admin":
        await cb.answer("Ruxsat yo'q", show_alert=True); return
    lang = user.get("lang", "uz")
    idea = await db.get_idea(idea_id)
    if not idea:
        await cb.answer("Topilmadi", show_alert=True); return

    await db.update_idea(idea_id, status=status)
    updated = await db.get_idea(idea_id)

    # Sheets sync
    try:
        from utils.sheets import sync_idea
        await sync_idea(updated)
    except Exception as e:
        logger.warning("sync_idea error: %s", e)

    # Muallif xabardor qilish
    status_label = _status_label(status, "uz")
    tip_label    = _type_label(idea.get("type"), "uz")
    try:
        await cb.bot.send_message(
            idea["tg_id"],
            f"💡 <b>G'oyangiz holati yangilandi!</b>\n"
            f"📌 {tip_label}: {idea['text'][:100]}\n"
            f"📊 Yangi holat: <b>{status_label}</b>",
            parse_mode="HTML",
        )
    except Exception:
        pass

    await cb.message.edit_text(
        _idea_text(updated, lang),
        reply_markup=idea_view_kb(lang, idea_id, status, is_admin=True),
        parse_mode="HTML",
    )
    await cb.answer(f"✅ {status_label}")


# ─── ADMIN: NOTE ─────────────────────────────────────────────────

@router.callback_query(F.data.startswith("idea:note:"))
async def idea_note_start(cb: CallbackQuery, state: FSMContext):
    idea_id = int(cb.data.split(":")[2])
    user    = await db.get_user(cb.from_user.id)
    if not user or user["role"] != "admin":
        await cb.answer("Ruxsat yo'q", show_alert=True); return
    lang = user.get("lang", "uz")
    await state.set_state(IdeaStates.waiting_admin_note)
    await state.update_data(idea_id=idea_id, lang=lang)
    await cb.message.answer(T(lang, "ideas_admin_note_ask"), parse_mode="HTML")
    await cb.answer()


@router.message(IdeaStates.waiting_admin_note)
async def idea_note_save(message: Message, state: FSMContext):
    data    = await state.get_data()
    idea_id = data.get("idea_id")
    lang    = data.get("lang", "uz")
    await state.clear()

    if message.text and message.text.strip() != "/skip":
        await db.update_idea(idea_id, admin_note=message.text.strip())

    updated = await db.get_idea(idea_id)
    if updated:
        try:
            from utils.sheets import sync_idea
            await sync_idea(updated)
        except Exception as e:
            logger.warning("sync_idea error: %s", e)

    await message.answer(
        T(lang, "ideas_admin_note_saved"),
        parse_mode="HTML",
        reply_markup=idea_view_kb(lang, idea_id, updated["status"] if updated else "new", is_admin=True),
    )
