"""Vaqt boshqaruvi: vaqt hisobi, pomodoro, kunlik reja, statistika, streak."""
import datetime
import logging
import re

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from keyboards.time_kb import (
    time_menu_kb, category_kb, active_track_kb,
    pomo_duration_kb, active_pomo_kb, plan_items_kb,
    blocks_menu_kb, block_category_kb, block_priority_kb,
    PRIORITY_EMOJI, PRIORITY_LABEL,
)
from utils.pomodoro import schedule_pomodoro
from utils.time_blocks import schedule_block_reminder, block_start_dt
from utils.time_stats import build_week_report, build_streak_card

logger = logging.getLogger(__name__)
router = Router()

MENU_TEXT = "⏱ <b>Vaqt boshqaruvi</b>\n\nKerakli bo'limni tanlang:"


class TrackFSM(StatesGroup):
    waiting_task_name = State()

class PomoFSM(StatesGroup):
    waiting_custom_minutes = State()
    waiting_task_name = State()

class PlanFSM(StatesGroup):
    waiting_items = State()


def _today():
    return datetime.datetime.now().strftime("%Y-%m-%d")


# ═══════════════ MENYU ═══════════════

async def open_menu(cb: CallbackQuery, state: FSMContext = None):
    if state:
        await state.clear()
    try:
        await cb.message.edit_text(MENU_TEXT, reply_markup=time_menu_kb(), parse_mode="HTML")
    except Exception:
        await cb.message.answer(MENU_TEXT, reply_markup=time_menu_kb(), parse_mode="HTML")


@router.callback_query(F.data == "tm:menu")
async def tm_menu_cb(cb: CallbackQuery, state: FSMContext):
    await open_menu(cb, state)
    await cb.answer()


# ═══════════════ VAQT HISOBI ═══════════════

@router.callback_query(F.data == "tm:track_start")
async def track_start(cb: CallbackQuery):
    active = await db.get_active_time_log(cb.from_user.id)
    if active:
        started = datetime.datetime.fromisoformat(active["start_time"])
        mins = int((datetime.datetime.now() - started).total_seconds() // 60)
        await cb.message.edit_text(
            f"⏱ Sizda faol ish bor:\n<b>{active['task_name']}</b> "
            f"({active['category']})\n⏳ {mins} daqiqadan beri\n\n"
            "Avval uni tugating:",
            reply_markup=active_track_kb(), parse_mode="HTML")
        await cb.answer()
        return
    await cb.message.edit_text(
        "🗂 Ish qaysi yo'nalishga tegishli?", reply_markup=category_kb(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("tm:cat:"))
async def track_category(cb: CallbackQuery, state: FSMContext):
    category = cb.data.split(":", 2)[2]
    await state.update_data(category=category)
    await state.set_state(TrackFSM.waiting_task_name)
    await cb.message.edit_text(
        f"✍️ <b>{category}</b> — qaysi ish ustida ishlayapsiz?\n"
        "Ish nomini yozing:", parse_mode="HTML")
    await cb.answer()


@router.message(TrackFSM.waiting_task_name)
async def track_task_name(message: Message, state: FSMContext):
    data = await state.get_data()
    category = data.get("category", "Boshqa")
    task = message.text.strip()
    await db.start_time_log(message.from_user.id, task, category)
    await state.clear()
    await message.answer(
        f"▶️ <b>Vaqt ketmoqda</b>\n\n"
        f"📌 {task}\n🗂 {category}\n🕒 Boshlandi: {datetime.datetime.now():%H:%M}\n\n"
        "Ish tugagach «⏹ Tugatish»ni bosing.",
        reply_markup=active_track_kb(), parse_mode="HTML")


@router.callback_query(F.data == "tm:track_stop")
async def track_stop(cb: CallbackQuery):
    log = await db.stop_time_log(cb.from_user.id)
    if not log:
        await cb.answer("Faol ish topilmadi.", show_alert=True)
        return
    dur_min = log["duration_seconds"] // 60
    points = max(1, round(dur_min / 60 * 5))   # ~1 soat = 5 ball
    await db.add_focus_points(cb.from_user.id, points)
    await db.touch_streak(cb.from_user.id)
    h, m = divmod(dur_min, 60)
    dur_str = f"{h} soat {m} daqiqa" if h else f"{m} daqiqa"
    total = await db.today_total_str(cb.from_user.id)
    await cb.message.edit_text(
        f"✅ <b>Ish yakunlandi</b>\n\n"
        f"📌 {log['task_name']}\n🗂 {log['category']}\n"
        f"⏱ Sarflandi: <b>{dur_str}</b>\n⭐ +{points} fokus ball\n\n"
        f"Bugungi jami: {total}",
        reply_markup=time_menu_kb(), parse_mode="HTML")
    await cb.answer("Saqlandi ✅")


# ═══════════════ POMODORO ═══════════════

@router.callback_query(F.data == "tm:pomo")
async def pomo_start(cb: CallbackQuery):
    active = await db.get_active_pomodoro(cb.from_user.id)
    if active:
        ends = datetime.datetime.fromisoformat(active["ends_at"])
        left = max(0, int((ends - datetime.datetime.now()).total_seconds() // 60))
        await cb.message.edit_text(
            f"🍅 Fokus davom etmoqda — <b>{left} daqiqa</b> qoldi\n\n"
            f"📌 {active['task_name'] or 'Ish'}",
            reply_markup=active_pomo_kb(), parse_mode="HTML")
        await cb.answer()
        return
    await cb.message.edit_text(
        "🍅 <b>Pomodoro fokus</b>\n\nDavomiylikni tanlang:",
        reply_markup=pomo_duration_kb(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("tm:pomo_dur:"))
async def pomo_duration(cb: CallbackQuery, state: FSMContext):
    val = cb.data.split(":", 2)[2]
    if val == "custom":
        await state.set_state(PomoFSM.waiting_custom_minutes)
        await cb.message.edit_text("✏️ Necha daqiqa? (5–120 oralig'ida raqam yozing)",
                                   parse_mode="HTML")
        await cb.answer()
        return
    await state.update_data(minutes=int(val))
    await state.set_state(PomoFSM.waiting_task_name)
    await cb.message.edit_text(
        f"🍅 {val} daqiqa.\n\nNima ustida fokuslanmoqchisiz?\n"
        "Qisqa yozing (yoki «-» yuboring):", parse_mode="HTML")
    await cb.answer()


@router.message(PomoFSM.waiting_custom_minutes)
async def pomo_custom(message: Message, state: FSMContext):
    if not message.text.isdigit() or not (5 <= int(message.text) <= 120):
        await message.answer("Iltimos, 5–120 oralig'ida raqam yuboring.")
        return
    await state.update_data(minutes=int(message.text))
    await state.set_state(PomoFSM.waiting_task_name)
    await message.answer("Nima ustida fokuslanmoqchisiz? Qisqa yozing (yoki «-»):")


@router.message(PomoFSM.waiting_task_name)
async def pomo_launch(message: Message, state: FSMContext, scheduler, bot):
    data = await state.get_data()
    minutes = data.get("minutes", 25)
    task = None if message.text.strip() == "-" else message.text.strip()
    ends_at = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
    session_id = await db.start_pomodoro(
        message.from_user.id, task, minutes, ends_at)
    schedule_pomodoro(scheduler, bot, message.from_user.id, session_id, ends_at)
    await state.clear()
    await message.answer(
        f"🍅 <b>Fokus boshlandi!</b>\n\n"
        f"📌 {task or 'Ish'}\n⏱ {minutes} daqiqa\n"
        f"🔔 {ends_at:%H:%M} da eslataman\n\n"
        "📵 Telefonni chetga qo'ying, faqat bitta ishga to'liq berilib ishlang.",
        reply_markup=active_pomo_kb(), parse_mode="HTML")


@router.callback_query(F.data == "tm:pomo_cancel")
async def pomo_cancel(cb: CallbackQuery, scheduler):
    session = await db.get_active_pomodoro(cb.from_user.id)
    if not session:
        await cb.answer("Faol pomodoro yo'q.", show_alert=True)
        return
    await db.cancel_pomodoro(session["id"])
    try:
        scheduler.remove_job(f"pomodoro_{session['id']}")
    except Exception:
        pass
    await cb.message.edit_text(
        "⏹ Pomodoro to'xtatildi. Zarari yo'q — keyingisida davom etamiz! 💪",
        reply_markup=time_menu_kb(), parse_mode="HTML")
    await cb.answer()


# ═══════════════ KUNLIK REJA ═══════════════

@router.callback_query(F.data == "tm:plan")
async def plan_show(cb: CallbackQuery):
    items = await db.get_plan_items(cb.from_user.id, _today())
    if not items:
        await cb.message.edit_text(
            "📋 <b>Bugungi reja yo'q</b>\n\n"
            "Kuningizni 3 ta eng muhim ish bilan boshlang — "
            "bu samaradorlikning eng kuchli odati.\n\n"
            "«➕ Yangi reja tuzish»ni bosing.",
            reply_markup=plan_items_kb([]), parse_mode="HTML")
    else:
        done = sum(1 for i in items if i["is_done"])
        await cb.message.edit_text(
            f"📋 <b>Bugungi reja</b> ({done}/{len(items)} bajarildi)\n\n"
            "Bajarganingizni belgilang:",
            reply_markup=plan_items_kb(items), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "tm:plan_new")
async def plan_new(cb: CallbackQuery, state: FSMContext):
    await state.set_state(PlanFSM.waiting_items)
    await cb.message.edit_text(
        "📝 Bugungi <b>3 ta asosiy ishingizni</b> yozing.\n"
        "Har birini yangi qatordan:\n\n"
        "<i>Masalan:\nDe Dietrich karusel reklamasini tayyorlash\n"
        "10 ta mahsulot kartochkasi SEO\nHaftalik hisobot</i>", parse_mode="HTML")
    await cb.answer()


@router.message(PlanFSM.waiting_items)
async def plan_save(message: Message, state: FSMContext):
    lines = [l.strip() for l in message.text.split("\n") if l.strip()][:3]
    if not lines:
        await message.answer("Kamida bitta ish yozing.")
        return
    await db.save_daily_plan(message.from_user.id, _today(), lines)
    await state.clear()
    items = await db.get_plan_items(message.from_user.id, _today())
    txt = "\n".join(f"{i+1}. {l}" for i, l in enumerate(lines))
    await message.answer(
        f"✅ <b>Bugungi reja tuzildi:</b>\n\n{txt}\n\n"
        "Kun davomida bajarganingizni belgilab boring. Omad! 🚀",
        reply_markup=plan_items_kb(items), parse_mode="HTML")


@router.callback_query(F.data.startswith("tm:toggle:"))
async def plan_toggle(cb: CallbackQuery):
    item_id = int(cb.data.split(":")[2])
    is_done = await db.toggle_plan_item(item_id)
    if is_done:
        await db.add_focus_points(cb.from_user.id, 5)
        await db.touch_streak(cb.from_user.id)
    items = await db.get_plan_items(cb.from_user.id, _today())
    done = sum(1 for i in items if i["is_done"])
    footer = ("🎉 Hammasi bajarildi! Zo'r ish!"
              if items and done == len(items) else "Bajarganingizni belgilang:")
    await cb.message.edit_text(
        f"📋 <b>Bugungi reja</b> ({done}/{len(items)} bajarildi)\n\n{footer}",
        reply_markup=plan_items_kb(items), parse_mode="HTML")
    await cb.answer("✅ +5 ball" if is_done else "Belgi olindi")


# ═══════════════ STATISTIKA / STREAK ═══════════════

@router.callback_query(F.data == "tm:stats")
async def stats_show(cb: CallbackQuery):
    text = await build_week_report(cb.from_user.id)
    await cb.message.edit_text(text, reply_markup=time_menu_kb(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "tm:streak")
async def streak_show(cb: CallbackQuery):
    text = await build_streak_card(cb.from_user.id)
    await cb.message.edit_text(text, reply_markup=time_menu_kb(), parse_mode="HTML")
    await cb.answer()


# ═══════════════ VAQT BLOKLARI (Stage 2) ═══════════════
STATUS_EMOJI = {"planned": "⬜️", "done": "✅", "skipped": "⏭"}


class BlockFSM(StatesGroup):
    title = State()
    category = State()
    priority = State()
    time_range = State()


def _parse_block_time(text: str):
    t = text.strip().replace(" ", "").replace("–", "-").replace("—", "-")
    m = re.match(r"^(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})$", t)
    if not m:
        return None
    h1, m1, h2, m2 = map(int, m.groups())
    if not (0 <= h1 < 24 and 0 <= m1 < 60 and 0 <= h2 < 24 and 0 <= m2 < 60):
        return None
    start, end = f"{h1:02d}:{m1:02d}", f"{h2:02d}:{m2:02d}"
    if end <= start:
        return None
    return start, end


def _render_blocks(blocks) -> str:
    if not blocks:
        return ("⏳ <b>Bugungi bloklar yo'q</b>\n\n"
                "Kuningizni oldindan bloklarga bo'ling — diqqatni "
                "jamlashning eng samarali usuli.\n\n"
                "Masalan:\n🔴 09:00–11:00  SEO audit\n"
                "🟡 11:00–12:00  Kontent\n🟢 14:00–16:00  Reklama")
    lines = ["⏳ <b>Bugungi vaqt bloklari</b>\n"]
    for b in blocks:
        prio = PRIORITY_EMOJI.get(b["priority"], "")
        stat = STATUS_EMOJI.get(b["status"], "")
        lines.append(f"{prio} {b['start_time']}–{b['end_time']}  "
                     f"{b['title']} {stat}")
    lines.append("\n<i>🔴 yuqori · 🟡 o'rta · 🟢 past</i>")
    return "\n".join(lines)


@router.callback_query(F.data == "tm:blocks")
async def blocks_show(cb: CallbackQuery):
    blocks = await db.get_blocks_for_day(cb.from_user.id, _today())
    await cb.message.edit_text(_render_blocks(blocks),
                               reply_markup=blocks_menu_kb(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "tm:block_add")
async def block_add(cb: CallbackQuery, state: FSMContext):
    await state.set_state(BlockFSM.title)
    await cb.message.edit_text(
        "✍️ Blok nomi?\n<i>(masalan: «De Dietrich reklamasi»)</i>",
        parse_mode="HTML")
    await cb.answer()


@router.message(BlockFSM.title)
async def block_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(BlockFSM.category)
    await message.answer("🗂 Kategoriya?", reply_markup=block_category_kb())


@router.callback_query(BlockFSM.category, F.data.startswith("tm:bcat:"))
async def block_category(cb: CallbackQuery, state: FSMContext):
    await state.update_data(category=cb.data.split(":", 2)[2])
    await state.set_state(BlockFSM.priority)
    await cb.message.edit_text("🎯 Muhimlik darajasi?",
                               reply_markup=block_priority_kb())
    await cb.answer()


@router.callback_query(BlockFSM.priority, F.data.startswith("tm:bprio:"))
async def block_priority(cb: CallbackQuery, state: FSMContext):
    await state.update_data(priority=cb.data.split(":", 2)[2])
    await state.set_state(BlockFSM.time_range)
    await cb.message.edit_text(
        "🕒 Vaqt oralig'ini yozing:\n\nFormat: <code>09:00-11:00</code>",
        parse_mode="HTML")
    await cb.answer()


@router.message(BlockFSM.time_range)
async def block_save(message: Message, state: FSMContext, scheduler, bot):
    parsed = _parse_block_time(message.text)
    if not parsed:
        await message.answer(
            "❌ Noto'g'ri format. Masalan: <code>09:00-11:00</code>\n"
            "(tugash vaqti boshlanishdan keyin bo'lsin)", parse_mode="HTML")
        return
    start, end = parsed
    data = await state.get_data()
    priority = data.get("priority", "medium")
    block_id = await db.add_time_block(
        message.from_user.id, _today(), data["title"],
        data.get("category", "Boshqa"), start, end, priority)

    run_dt = block_start_dt(_today(), start)
    if run_dt > datetime.datetime.now():
        schedule_block_reminder(scheduler, bot, message.from_user.id,
                                block_id, run_dt)

    await state.clear()
    blocks = await db.get_blocks_for_day(message.from_user.id, _today())
    prio = PRIORITY_EMOJI.get(priority, "")
    await message.answer(
        f"✅ Blok qo'shildi: {prio} {start}–{end}  {data['title']}\n\n"
        + _render_blocks(blocks),
        reply_markup=blocks_menu_kb(), parse_mode="HTML")


@router.callback_query(F.data.startswith("tm:bdone:"))
async def block_done(cb: CallbackQuery):
    block_id = int(cb.data.split(":")[2])
    await db.set_block_status(block_id, "done")
    await db.add_focus_points(cb.from_user.id, 5)
    await db.touch_streak(cb.from_user.id)
    try:
        await cb.message.edit_text(
            cb.message.html_text + "\n\n✅ <b>Bajarildi</b> (+5 ball)",
            parse_mode="HTML")
    except Exception:
        pass
    await cb.answer("Ajoyib! 🎯")


@router.callback_query(F.data.startswith("tm:bskip:"))
async def block_skip(cb: CallbackQuery):
    block_id = int(cb.data.split(":")[2])
    await db.set_block_status(block_id, "skipped")
    try:
        await cb.message.edit_text(
            cb.message.html_text + "\n\n⏭ <i>O'tkazib yuborildi</i>",
            parse_mode="HTML")
    except Exception:
        pass
    await cb.answer("Belgilandi")
