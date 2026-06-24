"""Kontent kalendar: SMM menejerlar uchun haftalik/oylik kontent rejasi."""
import datetime
import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

import database as db
from keyboards.kb import (
    content_menu_kb, content_platform_kb, content_type_kb,
    content_entry_kb, content_week_nav_kb, back_kb, assignee_kb
)
from texts import T

logger = logging.getLogger(__name__)
router = Router()

PLATFORM_ICONS = {
    "instagram": "📸", "telegram": "✈️", "tiktok": "🎵",
    "facebook": "👥", "youtube": "▶️",
}
TYPE_ICONS = {
    "post": "🖼", "story": "📖", "reels": "🎬",
    "carousel": "🎠", "video": "📹",
}
STATUS_ICONS = {
    "planned": "⏳", "done": "✅", "failed": "❌", "postponed": "🔄",
}
DAY_NAMES_UZ = ["Du", "Se", "Ch", "Pa", "Ju", "Sh", "Ya"]
DAY_NAMES_RU = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


class ContentStates(StatesGroup):
    date     = State()
    platform = State()
    ctype    = State()
    title    = State()
    note     = State()


def _week_range(offset=0):
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday()) + datetime.timedelta(weeks=offset)
    sunday = monday + datetime.timedelta(days=6)
    return monday, sunday


def _week_text(entries, monday, lang):
    day_names = DAY_NAMES_UZ if lang == "uz" else DAY_NAMES_RU
    lines = [T(lang, "content_week_title"),
             f"📅 {monday.strftime('%d.%m')} — {(monday + datetime.timedelta(6)).strftime('%d.%m')}\n"]
    by_day = {}
    for e in entries:
        d = e["plan_date"]
        by_day.setdefault(d, []).append(e)

    for i in range(7):
        day = monday + datetime.timedelta(days=i)
        day_str = day.isoformat()
        day_label = f"{day_names[i]} {day.strftime('%d.%m')}"
        day_entries = by_day.get(day_str, [])
        if not day_entries:
            lines.append(f"<b>{day_label}</b> — —")
        else:
            lines.append(f"<b>{day_label}</b>")
            for e in day_entries:
                picon = PLATFORM_ICONS.get(e["platform"], "📱")
                ticon = TYPE_ICONS.get(e["content_type"], "📄")
                sicon = STATUS_ICONS.get(e["status"], "⏳")
                title = e["title"][:25] if e["title"] else e["content_type"]
                lines.append(f"  {sicon}{picon}{ticon} {title}")
    return "\n".join(lines)


# ─── MENU ────────────────────────────────────────────────────────

@router.callback_query(F.data.in_({"go:content_menu", "content:menu"}))
async def content_menu(cb: CallbackQuery):
    user = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(); return
    lang     = user["lang"]
    is_admin = user["role"] == "admin"
    await cb.message.edit_text(
        T(lang, "content_menu_title"),
        reply_markup=content_menu_kb(lang, is_admin=is_admin),
        parse_mode="HTML",
    )
    await cb.answer()


# ─── WEEK VIEW ───────────────────────────────────────────────────

@router.callback_query(F.data.startswith("content:week:"))
async def content_week(cb: CallbackQuery):
    offset   = int(cb.data.split(":")[2])
    user     = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(); return
    lang     = user["lang"]
    is_admin = user["role"] == "admin"
    monday, sunday = _week_range(offset)
    entries = await db.get_content_entries(
        user_id=None if is_admin else user["id"],
        date_from=monday.isoformat(),
        date_to=sunday.isoformat(),
    )
    if not entries:
        text = f"{T(lang, 'content_week_title')}\n{monday.strftime('%d.%m')}–{sunday.strftime('%d.%m')}\n\n{T(lang, 'content_empty')}"
    else:
        text = _week_text(entries, monday, lang)

    # Inline entry buttons
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = []
    for e in entries:
        picon = PLATFORM_ICONS.get(e["platform"], "📱")
        sicon = STATUS_ICONS.get(e["status"], "⏳")
        day   = e["plan_date"][8:]  # DD
        title = (e["title"] or e["content_type"])[:20]
        name  = (e.get("user_name") or "").split()[0] if is_admin else ""
        rows.append([InlineKeyboardButton(
            text=f"{sicon}{picon} {day} {title}" + (f" | {name}" if name else ""),
            callback_data=f"content:entry:{e['id']}:{offset}"
        )])
    nav = []
    if offset < 0:
        nav.append(InlineKeyboardButton(text="▶️ Keyingi" if lang=="uz" else "▶️ Далее",
                                         callback_data=f"content:week:{offset+1}"))
    nav.append(InlineKeyboardButton(text="◀️ Oldingi" if lang=="uz" else "◀️ Назад",
                                     callback_data=f"content:week:{offset-1}"))
    rows.append(nav)
    rows.append([InlineKeyboardButton(text="➕ Qo'shish" if lang=="uz" else "➕ Добавить",
                                       callback_data="content:add")])
    rows.append([InlineKeyboardButton(text=T(lang, "back"), callback_data="go:content_menu")])
    await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
                                parse_mode="HTML")
    await cb.answer()


# ─── ENTRY VIEW ──────────────────────────────────────────────────

@router.callback_query(F.data.startswith("content:entry:"))
async def content_entry_view(cb: CallbackQuery):
    parts    = cb.data.split(":")
    entry_id = int(parts[2])
    offset   = int(parts[3]) if len(parts) > 3 else 0
    user     = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(); return
    lang  = user["lang"]
    entry = await db.get_content_entry(entry_id)
    if not entry:
        await cb.answer("Topilmadi", show_alert=True); return
    picon = PLATFORM_ICONS.get(entry["platform"], "📱")
    ticon = TYPE_ICONS.get(entry["content_type"], "📄")
    sicon = STATUS_ICONS.get(entry["status"], "⏳")
    text  = (
        f"{picon}{ticon} <b>{entry['title'] or entry['content_type']}</b>\n"
        f"📅 {entry['plan_date']}\n"
        f"📱 {entry['platform'].capitalize()} — {entry['content_type'].capitalize()}\n"
        f"Holat: {sicon} {entry['status'].capitalize()}"
    )
    if entry.get("note"):
        text += f"\n💬 {entry['note']}"
    await cb.message.edit_text(
        text,
        reply_markup=content_entry_kb(lang, entry_id, entry["status"], back_week=offset),
        parse_mode="HTML",
    )
    await cb.answer()


@router.callback_query(F.data.startswith("content:done:"))
async def content_mark_done(cb: CallbackQuery):
    entry_id = int(cb.data.split(":")[2])
    await db.update_content_entry(entry_id, status="done")
    user = await db.get_user(cb.from_user.id)
    lang = user["lang"] if user else "uz"
    await cb.answer(T(lang, "content_done"))
    cb.data = f"content:entry:{entry_id}:0"
    await content_entry_view(cb)


@router.callback_query(F.data.startswith("content:fail:"))
async def content_mark_failed(cb: CallbackQuery):
    entry_id = int(cb.data.split(":")[2])
    await db.update_content_entry(entry_id, status="failed")
    user = await db.get_user(cb.from_user.id)
    lang = user["lang"] if user else "uz"
    await cb.answer(T(lang, "content_failed"))
    cb.data = f"content:entry:{entry_id}:0"
    await content_entry_view(cb)


@router.callback_query(F.data.startswith("content:del:"))
async def content_delete(cb: CallbackQuery):
    entry_id = int(cb.data.split(":")[2])
    user     = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(); return
    await db.delete_content_entry(entry_id)
    await cb.answer("🗑 O'chirildi")
    cb.data = "content:week:0"
    await content_week(cb)


# ─── ADD CONTENT (FSM) ───────────────────────────────────────────

@router.callback_query(F.data == "content:add")
async def content_add_start(cb: CallbackQuery, state: FSMContext):
    user = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(); return
    lang     = user["lang"]
    is_admin = user["role"] == "admin"
    await state.set_state(ContentStates.date)
    await state.update_data(lang=lang, user_id=user["id"], is_admin=is_admin)
    await cb.message.answer(T(lang, "content_ask_date"), parse_mode="HTML",
                             reply_markup=back_kb(lang, "content_menu"))
    await cb.answer()


@router.message(ContentStates.date)
async def content_add_date(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    try:
        d = datetime.datetime.strptime(message.text.strip(), "%d.%m.%Y").date()
    except ValueError:
        await message.answer("❌ Sana formati: KK.OO.YYYY (masalan: 25.07.2025)")
        return
    await state.update_data(plan_date=d.isoformat())
    await state.set_state(ContentStates.platform)
    await message.answer(T(lang, "content_ask_platform"), parse_mode="HTML",
                          reply_markup=content_platform_kb())


@router.callback_query(ContentStates.platform, F.data.startswith("cplt:"))
async def content_add_platform(cb: CallbackQuery, state: FSMContext):
    platform = cb.data.split(":")[1]
    data     = await state.get_data()
    lang     = data.get("lang", "uz")
    await state.update_data(platform=platform)
    await state.set_state(ContentStates.ctype)
    await cb.message.edit_text(T(lang, "content_ask_type"), parse_mode="HTML",
                                reply_markup=content_type_kb())
    await cb.answer()


@router.callback_query(ContentStates.ctype, F.data.startswith("ctype:"))
async def content_add_type(cb: CallbackQuery, state: FSMContext):
    ctype = cb.data.split(":")[1]
    data  = await state.get_data()
    lang  = data.get("lang", "uz")
    await state.update_data(content_type=ctype)
    await state.set_state(ContentStates.title)
    await cb.message.edit_text(T(lang, "content_ask_title"), parse_mode="HTML")
    await cb.answer()


@router.message(ContentStates.title)
async def content_add_title(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(title=message.text.strip())
    await state.set_state(ContentStates.note)
    await message.answer(T(lang, "content_ask_note"), parse_mode="HTML",
                          reply_markup=back_kb(lang, "content_menu"))


@router.message(ContentStates.note)
async def content_add_note(message: Message, state: FSMContext):
    data  = await state.get_data()
    lang  = data.get("lang", "uz")
    note  = "" if message.text.strip() == "/skip" else message.text.strip()
    entry_id = await db.create_content_entry(
        user_id      = data["user_id"],
        plan_date    = data["plan_date"],
        platform     = data["platform"],
        content_type = data["content_type"],
        title        = data["title"],
        created_by   = message.from_user.id,
        note         = note,
    )
    await state.clear()
    picon = PLATFORM_ICONS.get(data["platform"], "📱")
    ticon = TYPE_ICONS.get(data["content_type"], "📄")
    await message.answer(
        f"✅ {T(lang, 'content_saved')}\n"
        f"{picon}{ticon} {data['title']}\n"
        f"📅 {data['plan_date']}",
        parse_mode="HTML",
        reply_markup=content_menu_kb(lang, is_admin=data.get("is_admin", False)),
    )


# ─── STATS ───────────────────────────────────────────────────────

@router.callback_query(F.data == "content:stats")
async def content_stats(cb: CallbackQuery):
    user = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(); return
    lang     = user["lang"]
    now      = datetime.datetime.now()
    stats    = await db.get_content_stats(user["id"], now.month, now.year)
    by_st    = stats["by_status"]
    by_pl    = stats["by_platform"]
    total    = sum(by_st.values())
    done     = by_st.get("done", 0)
    planned  = by_st.get("planned", 0)
    failed   = by_st.get("failed", 0)
    pct      = round(done / total * 100) if total else 0
    bar      = "█" * round(pct / 10) + "░" * (10 - round(pct / 10))
    text = (
        f"📊 <b>Kontent statistikasi</b>\n"
        f"📅 {now.month}/{now.year}\n\n"
        f"Jami: {total} ta\n"
        f"✅ Bajarildi: {done}\n"
        f"⏳ Rejalashtirildi: {planned}\n"
        f"❌ Bajarilmadi: {failed}\n\n"
        f"📈 {bar} {pct}%\n\n"
    )
    if by_pl:
        text += "<b>Platformalar bo'yicha (bajarildi):</b>\n"
        for pl, cnt in sorted(by_pl.items(), key=lambda x: -x[1]):
            icon = PLATFORM_ICONS.get(pl, "📱")
            text += f"{icon} {pl.capitalize()}: {cnt}\n"
    await cb.message.edit_text(text, reply_markup=back_kb(lang, "content_menu"), parse_mode="HTML")
    await cb.answer()
