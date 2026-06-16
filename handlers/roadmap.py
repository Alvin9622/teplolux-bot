import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
import utils.sheets as sheets
from config import ADMIN_IDS
from keyboards.kb import roadmap_menu_kb, roadmap_phase_kb, roadmap_phase_select_kb, back_kb, roadmap_task_ext_kb
from texts import T

router = Router()

PHASES = {"1-3": "roadmap_phase_1_3", "4-6": "roadmap_phase_4_6",
          "7-9": "roadmap_phase_7_9", "10-18": "roadmap_phase_10_18"}


def _progress_bar(done, total, width=10):
    if total == 0:
        return "░" * width + " 0/0"
    filled = round(done / total * width)
    filled = max(0, min(width, filled))
    return "█" * filled + "░" * (width - filled) + f" {done}/{total} ({round(done/total*100)}%)"


class RMStates(StatesGroup):
    add_phase    = State()
    add_title    = State()
    add_notes    = State()
    add_deadline = State()
    add_assignee = State()
    edit_value   = State()


def is_admin(user):
    return user and (user["role"] == "admin" or user["telegram_id"] in ADMIN_IDS)


async def _get_ul(tg_id):
    user = await db.get_user(tg_id)
    return user, (user["lang"] if user else "uz")


def _task_card(task, lang):
    phase_key = PHASES.get(task["phase"], "roadmap_phase_1_3")
    status_icon = "✅ Bajarildi" if task["status"] == "done" else "⬜ Kutilmoqda"
    lines = [
        T(lang, phase_key),
        "",
        f"<b>{task['title']}</b>",
    ]
    if task.get("notes"):
        lines.append(f"📝 {task['notes']}")
    if task.get("deadline"):
        lines.append(f"📅 {task['deadline']}")
    if task.get("assignee_name"):
        lines.append(f"👤 {task['assignee_name']}")
    lines.append(f"\nHolat: {status_icon}")
    return "\n".join(lines)


async def _show_menu(cb: CallbackQuery, lang: str):
    all_tasks = await db.get_roadmap_tasks()
    lines = [T(lang, "roadmap_menu"), ""]

    total_done = 0
    total_all = 0
    phase_labels = {
        "1-3":   "Bosqich 1-3" if lang == "uz" else "Этап 1-3",
        "4-6":   "Bosqich 4-6" if lang == "uz" else "Этап 4-6",
        "7-9":   "Bosqich 7-9" if lang == "uz" else "Этап 7-9",
        "10-18": "Bosqich 10-18" if lang == "uz" else "Этап 10-18",
    }
    for phase in ("1-3", "4-6", "7-9", "10-18"):
        tasks = [t for t in all_tasks if t["phase"] == phase]
        d = sum(1 for t in tasks if t["status"] == "done")
        t = len(tasks)
        total_done += d
        total_all += t
        label = phase_labels[phase]
        bar = _progress_bar(d, t)
        lines.append(f"{label}: {bar}")

    overall = _progress_bar(total_done, total_all)
    lbl = "Umumiy" if lang == "uz" else "Итого"
    lines.append(f"\n{lbl}: {overall}")

    text = "\n".join(lines)
    try:
        await cb.message.edit_text(text, reply_markup=roadmap_menu_kb(lang), parse_mode="HTML")
    except Exception:
        await cb.message.answer(text, reply_markup=roadmap_menu_kb(lang), parse_mode="HTML")
    await cb.answer()


async def _show_phase(cb: CallbackQuery, phase: str, lang: str):
    tasks = await db.get_roadmap_tasks(phase)
    phase_key = PHASES.get(phase, "roadmap_phase_1_3")
    done = sum(1 for t in tasks if t["status"] == "done")
    total = len(tasks)
    bar = _progress_bar(done, total)
    text = f"{T(lang, phase_key)}\n\n📊 {bar}"
    kb = roadmap_phase_kb(lang, tasks, phase)
    try:
        await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await cb.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "rm:menu")
async def rm_menu(cb: CallbackQuery):
    user, lang = await _get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    await _show_menu(cb, lang)


@router.callback_query(F.data.startswith("rm:phase:"))
async def rm_phase(cb: CallbackQuery):
    user, lang = await _get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    phase = cb.data.split(":")[2]
    await _show_phase(cb, phase, lang)


@router.callback_query(F.data.startswith("rm:task:"))
async def rm_task(cb: CallbackQuery):
    user, lang = await _get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    task_id = int(cb.data.split(":")[2])
    task = await db.get_roadmap_task(task_id)
    if not task:
        await cb.answer(T(lang, "error"), show_alert=True)
        return
    text = _task_card(task, lang)
    kb = roadmap_task_ext_kb(lang, task)
    try:
        await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await cb.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("rm:done:"))
async def rm_toggle_done(cb: CallbackQuery):
    user, lang = await _get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    task_id = int(cb.data.split(":")[2])
    task = await db.get_roadmap_task(task_id)
    if not task:
        await cb.answer(T(lang, "error"), show_alert=True)
        return
    old_status = task["status"]
    new_status = "done" if old_status == "pending" else "pending"
    await db.update_roadmap_task(task_id, status=new_status)
    # Activity log
    try:
        await db.log_activity_db("roadmap", task_id, "status_changed",
                                 user["id"] if user else None, old_status, new_status)
    except Exception:
        pass
    task = await db.get_roadmap_task(task_id)
    try:
        await sheets.sync_roadmap_task(task)
    except Exception:
        pass
    await cb.answer("✅" if new_status == "done" else "⬜")
    text = _task_card(task, lang)
    kb = roadmap_task_ext_kb(lang, task)
    try:
        await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass


@router.callback_query(F.data == "rm:add")
async def rm_add_start(cb: CallbackQuery, state: FSMContext):
    user, lang = await _get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    await state.update_data(lang=lang, user_id=user["id"])
    await state.set_state(RMStates.add_phase)
    try:
        await cb.message.edit_text(T(lang, "roadmap_ask_phase"), reply_markup=roadmap_phase_select_kb(lang), parse_mode="HTML")
    except Exception:
        await cb.message.answer(T(lang, "roadmap_ask_phase"), reply_markup=roadmap_phase_select_kb(lang), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("rm:add:"))
async def rm_add_phase_preset(cb: CallbackQuery, state: FSMContext):
    user, lang = await _get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    phase = cb.data.split(":")[2]
    await state.update_data(lang=lang, user_id=user["id"], phase=phase)
    await state.set_state(RMStates.add_title)
    await cb.message.answer(T(lang, "roadmap_ask_title", cancel=T(lang, "cancel_action")), parse_mode="HTML")
    await cb.answer()


@router.callback_query(RMStates.add_phase, F.data.startswith("rm:newphase:"))
async def rm_add_phase(cb: CallbackQuery, state: FSMContext):
    phase = cb.data.split(":")[2]
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(phase=phase)
    await state.set_state(RMStates.add_title)
    await cb.message.answer(T(lang, "roadmap_ask_title", cancel=T(lang, "cancel_action")), parse_mode="HTML")
    await cb.answer()


@router.message(RMStates.add_title)
async def rm_add_title(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(title=msg.text.strip())
    await state.set_state(RMStates.add_notes)
    await msg.answer(T(lang, "roadmap_ask_notes", cancel=T(lang, "cancel_action")), parse_mode="HTML")


@router.message(RMStates.add_notes)
async def rm_add_notes(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    notes = "" if msg.text.strip() == "/skip" else msg.text.strip()
    await state.update_data(notes=notes)
    await state.set_state(RMStates.add_deadline)
    await msg.answer(T(lang, "roadmap_ask_deadline"), parse_mode="HTML")


@router.message(RMStates.add_deadline)
async def rm_add_deadline(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    text = msg.text.strip()
    deadline = ""
    if text != "/skip":
        try:
            parts = text.split(".")
            iso = f"{parts[2]}-{parts[1]}-{parts[0]}"
            datetime.date.fromisoformat(iso)
            deadline = iso
        except Exception:
            await msg.answer(T(lang, "invalid_date"))
            return
    await state.update_data(deadline=deadline)
    await state.set_state(RMStates.add_assignee)
    await msg.answer(T(lang, "roadmap_ask_assignee"), parse_mode="HTML")


@router.message(RMStates.add_assignee)
async def rm_add_assignee(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    assignee = "" if msg.text.strip() == "/skip" else msg.text.strip()
    await state.clear()
    task_id = await db.create_roadmap_task(
        phase=data["phase"], title=data["title"],
        notes=data.get("notes", ""), created_by=data.get("user_id")
    )
    # Update with deadline and assignee_name
    update_kwargs = {}
    if data.get("deadline"):
        update_kwargs["deadline"] = data["deadline"]
    if assignee:
        update_kwargs["assignee_name"] = assignee
    if update_kwargs:
        await db.update_roadmap_task(task_id, **update_kwargs)
    task = await db.get_roadmap_task(task_id)
    try:
        await db.log_activity_db("roadmap", task_id, "created",
                                 data.get("user_id"), "", data["title"])
    except Exception:
        pass
    try:
        await sheets.sync_roadmap_task(task)
    except Exception:
        pass
    await msg.answer(
        T(lang, "roadmap_added"),
        reply_markup=back_kb(lang, f"rm_phase_{data['phase']}"),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("rm:edit:"))
async def rm_edit_start(cb: CallbackQuery, state: FSMContext):
    user, lang = await _get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    parts = cb.data.split(":")
    field = parts[2]
    task_id = int(parts[3])
    task = await db.get_roadmap_task(task_id)
    if not task:
        await cb.answer(T(lang, "error"), show_alert=True)
        return
    await state.update_data(lang=lang, rm_task_id=task_id, rm_field=field,
                            user_id=user["id"] if user else None)
    await state.set_state(RMStates.edit_value)
    ask_map = {
        "title":         "roadmap_ask_edit_title",
        "notes":         "roadmap_ask_edit_notes",
        "deadline":      "roadmap_ask_deadline",
        "assignee_name": "roadmap_ask_assignee",
    }
    ask_key = ask_map.get(field, "roadmap_ask_edit_title")
    await cb.message.answer(T(lang, ask_key), parse_mode="HTML")
    await cb.answer()


@router.message(RMStates.edit_value)
async def rm_edit_value(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    task_id = data["rm_task_id"]
    field = data["rm_field"]
    await state.clear()
    raw = msg.text.strip()
    # For deadline, convert DD.MM.YYYY -> YYYY-MM-DD
    if field == "deadline" and raw != "/skip":
        try:
            parts = raw.split(".")
            raw = f"{parts[2]}-{parts[1]}-{parts[0]}"
            datetime.date.fromisoformat(raw)
        except Exception:
            await msg.answer(T(lang, "invalid_date"))
            return
    value = "" if raw == "/skip" else raw
    task_before = await db.get_roadmap_task(task_id)
    old_val = (task_before.get(field) or "") if task_before else ""
    await db.update_roadmap_task(task_id, **{field: value})
    task = await db.get_roadmap_task(task_id)
    try:
        await db.log_activity_db("roadmap", task_id, f"edit_{field}",
                                 data.get("user_id"), old_val, value)
    except Exception:
        pass
    try:
        await sheets.sync_roadmap_task(task)
    except Exception:
        pass
    await msg.answer(
        T(lang, "roadmap_updated"),
        reply_markup=back_kb(lang, f"rm_phase_{task['phase']}"),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("rm:del:"))
async def rm_delete(cb: CallbackQuery):
    user, lang = await _get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    task_id = int(cb.data.split(":")[2])
    task = await db.get_roadmap_task(task_id)
    if not task:
        await cb.answer(T(lang, "error"), show_alert=True)
        return
    phase = task["phase"]
    title = task.get("title", "")
    await db.delete_roadmap_task(task_id)
    try:
        await db.log_activity_db("roadmap", task_id, "deleted",
                                 user["id"] if user else None, title, "")
    except Exception:
        pass
    try:
        await sheets.delete_roadmap_from_sheet(task_id)
    except Exception:
        pass
    await cb.answer(T(lang, "roadmap_deleted"))
    tasks = await db.get_roadmap_tasks(phase)
    phase_key = PHASES.get(phase, "roadmap_phase_1_3")
    done = sum(1 for t in tasks if t["status"] == "done")
    total = len(tasks)
    bar = _progress_bar(done, total)
    text = f"{T(lang, phase_key)}\n\n📊 {bar}"
    try:
        await cb.message.edit_text(text, reply_markup=roadmap_phase_kb(lang, tasks, phase), parse_mode="HTML")
    except Exception:
        await cb.message.answer(text, reply_markup=roadmap_phase_kb(lang, tasks, phase), parse_mode="HTML")
