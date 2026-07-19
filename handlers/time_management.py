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
    templates_menu_kb, template_detail_kb, weekday_picker_kb, WEEKDAYS_UZ,
    goals_menu_kb, goal_kind_kb, goal_category_kb, goal_detail_kb,
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


# ═══════════════ BLOK SHABLONLARI (Stage 3) ═══════════════
class TemplateFSM(StatesGroup):
    save_name = State()

class WeekdayFSM(StatesGroup):
    selecting = State()


def _render_template_detail(tpl, items) -> str:
    lines = [f"📁 <b>{tpl['name']}</b>\n"]
    for it in items:
        prio = PRIORITY_EMOJI.get(it["priority"], "")
        lines.append(f"{prio} {it['start_time']}–{it['end_time']}  {it['title']}")
    if tpl["auto_weekdays"]:
        days = [WEEKDAYS_UZ[int(x)] for x in tpl["auto_weekdays"].split(",") if x != ""]
        lines.append(f"\n🔁 Avtomatik: {', '.join(days)}")
    else:
        lines.append("\n🔁 Avtomatik: o'chirilgan")
    return "\n".join(lines)


@router.callback_query(F.data == "tm:templates")
async def templates_show(cb: CallbackQuery):
    tpls = await db.get_templates(cb.from_user.id)
    if not tpls:
        txt = ("📁 <b>Shablonlar yo'q</b>\n\n"
               "Har kuni bir xil bloklarni qayta yaratmang — bir marta "
               "shablon qiling, keyin bir tugma bilan qo'llang.\n\n"
               "Bugungi bloklaringizni «💾 Shablon qilish» orqali saqlang.")
    else:
        txt = "📁 <b>Shablonlar</b>\n\n🔁 = avtomatik qo'llanadigan"
    await cb.message.edit_text(txt, reply_markup=templates_menu_kb(tpls), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "tm:tpl_save")
async def tpl_save_start(cb: CallbackQuery, state: FSMContext):
    blocks = await db.get_blocks_for_day(cb.from_user.id, _today())
    if not blocks:
        await cb.answer("Bugun bloklar yo'q — avval blok qo'shing.", show_alert=True)
        return
    await state.set_state(TemplateFSM.save_name)
    await cb.message.edit_text(
        f"💾 Bugungi {len(blocks)} ta blokni shablon qilamiz.\n\n"
        "Shablon nomini yozing (masalan: «Ish kuni»):", parse_mode="HTML")
    await cb.answer()


@router.message(TemplateFSM.save_name)
async def tpl_save_finish(message: Message, state: FSMContext):
    name = message.text.strip()
    await db.save_blocks_as_template(message.from_user.id, name, _today())
    await state.clear()
    tpls = await db.get_templates(message.from_user.id)
    await message.answer(
        f"✅ «{name}» shabloni saqlandi.\n\n"
        "Endi uni istalgan kuni bir tugma bilan qo'llashingiz mumkin.",
        reply_markup=templates_menu_kb(tpls), parse_mode="HTML")


@router.callback_query(F.data.startswith("tm:tpl_apply:"))
async def tpl_apply(cb: CallbackQuery, scheduler, bot):
    tid = int(cb.data.split(":")[2])
    created = await db.apply_template(cb.from_user.id, tid, _today())
    now = datetime.datetime.now()
    for b in created:
        run_dt = block_start_dt(_today(), b["start_time"])
        if run_dt > now:
            schedule_block_reminder(scheduler, bot, cb.from_user.id, b["id"], run_dt)
    blocks = await db.get_blocks_for_day(cb.from_user.id, _today())
    await cb.message.edit_text(
        f"✅ {len(created)} ta blok bugunga qo'shildi!\n\n" + _render_blocks(blocks),
        reply_markup=blocks_menu_kb(), parse_mode="HTML")
    await cb.answer("Qo'llandi 🎯")


@router.callback_query(F.data.startswith("tm:tpl_del:"))
async def tpl_del(cb: CallbackQuery):
    tid = int(cb.data.split(":")[2])
    await db.delete_template(tid)
    tpls = await db.get_templates(cb.from_user.id)
    await cb.message.edit_text("🗑 Shablon o'chirildi.",
                               reply_markup=templates_menu_kb(tpls), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("tm:tpl_days:"))
async def tpl_days(cb: CallbackQuery, state: FSMContext):
    tid = int(cb.data.split(":")[2])
    tpl = await db.get_template(tid)
    selected = [int(x) for x in tpl["auto_weekdays"].split(",") if x != ""]
    await state.set_state(WeekdayFSM.selecting)
    await state.update_data(template_id=tid, selected=selected)
    await cb.message.edit_text(
        "🔁 <b>Avtomatik qo'llash kunlari</b>\n\n"
        "Tanlangan kunlari ertalab (07:30) shablon avtomatik qo'llanadi. "
        "Kunlarni belgilang:",
        reply_markup=weekday_picker_kb(tid, selected), parse_mode="HTML")
    await cb.answer()


@router.callback_query(WeekdayFSM.selecting, F.data.startswith("tm:wd:"))
async def tpl_wd_toggle(cb: CallbackQuery, state: FSMContext):
    day = int(cb.data.split(":")[2])
    data = await state.get_data()
    selected = set(data["selected"])
    selected.symmetric_difference_update({day})
    selected = sorted(selected)
    await state.update_data(selected=selected)
    await cb.message.edit_reply_markup(
        reply_markup=weekday_picker_kb(data["template_id"], selected))
    await cb.answer()


@router.callback_query(WeekdayFSM.selecting, F.data == "tm:wd_save")
async def tpl_wd_save(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    tid = data["template_id"]
    await db.set_template_weekdays(tid, ",".join(str(d) for d in data["selected"]))
    await state.clear()
    tpl = await db.get_template(tid)
    items = await db.get_template_items(tid)
    await cb.message.edit_text(_render_template_detail(tpl, items),
                               reply_markup=template_detail_kb(tid), parse_mode="HTML")
    await cb.answer("Saqlandi ✅")


@router.callback_query(F.data.startswith("tm:tpl:"))
async def tpl_detail(cb: CallbackQuery):
    tid = int(cb.data.split(":")[2])
    tpl = await db.get_template(tid)
    items = await db.get_template_items(tid)
    await cb.message.edit_text(_render_template_detail(tpl, items),
                               reply_markup=template_detail_kb(tid), parse_mode="HTML")
    await cb.answer()


# ═══════════════ MAQSADLAR (Stage 3) ═══════════════
class GoalFSM(StatesGroup):
    title = State()
    kind = State()
    counter_target = State()
    counter_unit = State()
    time_category = State()
    time_hours = State()
    set_value = State()


def _is_number(s):
    try:
        float(s.replace(",", "."))
        return True
    except (ValueError, AttributeError):
        return False


async def _render_goal_detail(goal) -> str:
    current = await db.compute_goal_current(goal)
    target = goal["target_value"]
    pct = min(100, round(current / target * 100)) if target else 0
    filled = min(10, round(current / target * 10)) if target else 0
    bar_s = "▰" * filled + "▱" * (10 - filled)
    kind_label = "⏱ Vaqt maqsadi" if goal["kind"] == "time" else "📊 Sanoq maqsadi"
    lines = [f"🎯 <b>{goal['title']}</b>", kind_label]
    if goal["kind"] == "time":
        lines.append(f"🗂 {goal['category']} · {goal['period']}")
    lines.append(f"\n{bar_s}  {pct}%")
    lines.append(f"{current:g} / {target:g} {goal['unit']}")
    if pct >= 100:
        lines.append("\n🎉 Maqsadga erishildi! «✅ Bajarildi»ni bosing.")
    return "\n".join(lines)


@router.callback_query(F.data == "tm:goals")
async def goals_show(cb: CallbackQuery):
    goals = await db.get_goals(cb.from_user.id)
    if not goals:
        txt = ("🎯 <b>Maqsadlar yo'q</b>\n\n"
               "Kundalik ishni kattaroq maqsadga bog'lang:\n"
               "• 50 ta mahsulot kartochkasi SEO (sanoq)\n"
               "• Iyulda 40 soat kontent (vaqt — avtomatik hisoblanadi)\n\n"
               "«➕ Yangi maqsad» bilan boshlang.")
    else:
        txt = "🎯 <b>Maqsadlaringiz</b>\n\nBatafsil ko'rish uchun tanlang:"
    await cb.message.edit_text(txt, reply_markup=goals_menu_kb(goals), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "tm:goal_new")
async def goal_new(cb: CallbackQuery, state: FSMContext):
    await state.set_state(GoalFSM.title)
    await cb.message.edit_text(
        "🎯 Maqsad nomi?\n<i>(masalan: «Mahsulot kartochkalari SEO»)</i>",
        parse_mode="HTML")
    await cb.answer()


@router.message(GoalFSM.title)
async def goal_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(GoalFSM.kind)
    await message.answer("Maqsad turi?", reply_markup=goal_kind_kb())


@router.callback_query(GoalFSM.kind, F.data.startswith("tm:gkind:"))
async def goal_kind(cb: CallbackQuery, state: FSMContext):
    kind = cb.data.split(":")[2]
    await state.update_data(kind=kind)
    if kind == "counter":
        await state.set_state(GoalFSM.counter_target)
        await cb.message.edit_text("📊 Nechta? (maqsad soni, masalan: 50)", parse_mode="HTML")
    else:
        await state.set_state(GoalFSM.time_category)
        await cb.message.edit_text("⏱ Qaysi yo'nalish bo'yicha?",
                                   reply_markup=goal_category_kb(), parse_mode="HTML")
    await cb.answer()


@router.message(GoalFSM.counter_target)
async def goal_counter_target(message: Message, state: FSMContext):
    if not _is_number(message.text):
        await message.answer("Iltimos, raqam yuboring (masalan: 50).")
        return
    await state.update_data(target=float(message.text.replace(",", ".")))
    await state.set_state(GoalFSM.counter_unit)
    await message.answer("Birlik nomi? (masalan: «ta», «dona»)\n"
                         "Kerak bo'lmasa «-» yuboring:")


@router.message(GoalFSM.counter_unit)
async def goal_counter_unit(message: Message, state: FSMContext):
    unit = "" if message.text.strip() == "-" else message.text.strip()
    data = await state.get_data()
    await db.add_goal(message.from_user.id, data["title"], "counter",
                      data["target"], unit, None, None, None)
    await state.clear()
    goals = await db.get_goals(message.from_user.id)
    await message.answer("✅ Maqsad qo'shildi!", reply_markup=goals_menu_kb(goals),
                         parse_mode="HTML")


@router.callback_query(GoalFSM.time_category, F.data.startswith("tm:gcat:"))
async def goal_time_category(cb: CallbackQuery, state: FSMContext):
    await state.update_data(category=cb.data.split(":")[2])
    await state.set_state(GoalFSM.time_hours)
    await cb.message.edit_text("⏱ Necha soat? (bu oy uchun maqsad, masalan: 40)",
                               parse_mode="HTML")
    await cb.answer()


@router.message(GoalFSM.time_hours)
async def goal_time_hours(message: Message, state: FSMContext):
    if not _is_number(message.text):
        await message.answer("Iltimos, raqam yuboring (masalan: 40).")
        return
    data = await state.get_data()
    period = datetime.datetime.now().strftime("%Y-%m")
    await db.add_goal(message.from_user.id, data["title"], "time",
                      float(message.text.replace(",", ".")), "soat",
                      data["category"], period, None)
    await state.clear()
    goals = await db.get_goals(message.from_user.id)
    await message.answer(
        "✅ Vaqt maqsadi qo'shildi!\n"
        "<i>Progress vaqt loglaringizdan avtomatik hisoblanadi.</i>",
        reply_markup=goals_menu_kb(goals), parse_mode="HTML")


@router.callback_query(F.data.startswith("tm:ginc:"))
async def goal_inc(cb: CallbackQuery):
    _, _, gid, delta = cb.data.split(":")
    await db.update_goal_progress(int(gid), float(delta))
    goal = await db.get_goal(int(gid))
    await cb.message.edit_text(await _render_goal_detail(goal),
                               reply_markup=goal_detail_kb(goal), parse_mode="HTML")
    await cb.answer(f"+{delta} ✅")


@router.callback_query(F.data.startswith("tm:gset:"))
async def goal_set_start(cb: CallbackQuery, state: FSMContext):
    gid = int(cb.data.split(":")[2])
    await state.set_state(GoalFSM.set_value)
    await state.update_data(goal_id=gid)
    await cb.message.edit_text("✏️ Joriy qiymatni yozing (masalan: 23):", parse_mode="HTML")
    await cb.answer()


@router.message(GoalFSM.set_value)
async def goal_set_finish(message: Message, state: FSMContext):
    if not _is_number(message.text):
        await message.answer("Raqam yuboring.")
        return
    data = await state.get_data()
    await db.set_goal_value(data["goal_id"], float(message.text.replace(",", ".")))
    await state.clear()
    goal = await db.get_goal(data["goal_id"])
    await message.answer(await _render_goal_detail(goal),
                         reply_markup=goal_detail_kb(goal), parse_mode="HTML")


@router.callback_query(F.data.startswith("tm:gdone:"))
async def goal_done(cb: CallbackQuery):
    gid = int(cb.data.split(":")[2])
    await db.set_goal_status(gid, "done")
    await db.add_focus_points(cb.from_user.id, 20)
    goals = await db.get_goals(cb.from_user.id)
    await cb.message.edit_text(
        "🎉 <b>Maqsad bajarildi!</b> +20 fokus ball\n\nZo'r natija! 🏆",
        reply_markup=goals_menu_kb(goals), parse_mode="HTML")
    await cb.answer("Tabriklaymiz! 🎉")


@router.callback_query(F.data.startswith("tm:gdel:"))
async def goal_del(cb: CallbackQuery):
    gid = int(cb.data.split(":")[2])
    await db.delete_goal(gid)
    goals = await db.get_goals(cb.from_user.id)
    await cb.message.edit_text("🗑 Maqsad o'chirildi.",
                               reply_markup=goals_menu_kb(goals), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("tm:goal:"))
async def goal_detail(cb: CallbackQuery):
    gid = int(cb.data.split(":")[2])
    goal = await db.get_goal(gid)
    if not goal:
        await cb.answer("Topilmadi.", show_alert=True)
        return
    await cb.message.edit_text(await _render_goal_detail(goal),
                               reply_markup=goal_detail_kb(goal), parse_mode="HTML")
    await cb.answer()


# ═══════════════ EXCEL EKSPORT (Stage 3) ═══════════════
@router.callback_query(F.data == "tm:export")
async def export_excel(cb: CallbackQuery, bot):
    from aiogram.types import BufferedInputFile
    from utils.export import build_excel_report
    await cb.answer("Hisobot tayyorlanmoqda...")
    data = await build_excel_report(cb.from_user.id)
    fname = f"samaradorlik_{datetime.datetime.now():%Y%m%d}.xlsx"
    await bot.send_document(
        cb.from_user.id, BufferedInputFile(data, fname),
        caption="📊 <b>Shaxsiy samaradorlik hisoboti</b>\n"
                "Umumiy · Vaqt loglari (30 kun) · Maqsadlar",
        parse_mode="HTML")
