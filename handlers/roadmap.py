from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
import utils.sheets as sheets
from config import ADMIN_IDS
from keyboards.kb import roadmap_menu_kb, roadmap_phase_kb, roadmap_task_kb, roadmap_phase_select_kb, back_kb
from texts import T

router = Router()

PHASES = {"1-3": "roadmap_phase_1_3", "4-6": "roadmap_phase_4_6",
          "7-9": "roadmap_phase_7_9", "10-18": "roadmap_phase_10_18"}


class RMStates(StatesGroup):
    add_phase  = State()
    add_title  = State()
    add_notes  = State()
    edit_value = State()


def is_admin(user):
    return user and (user["role"] == "admin" or user["telegram_id"] in ADMIN_IDS)


async def _get_ul(tg_id):
    user = await db.get_user(tg_id)
    return user, (user["lang"] if user else "uz")


async def _show_menu(cb: CallbackQuery, lang: str):
    try:
        await cb.message.edit_text(T(lang, "roadmap_menu"), reply_markup=roadmap_menu_kb(lang), parse_mode="HTML")
    except Exception:
        await cb.message.answer(T(lang, "roadmap_menu"), reply_markup=roadmap_menu_kb(lang), parse_mode="HTML")
    await cb.answer()


async def _show_phase(cb: CallbackQuery, phase: str, lang: str):
    tasks = await db.get_roadmap_tasks(phase)
    phase_key = PHASES.get(phase, "roadmap_phase_1_3")
    done = sum(1 for t in tasks if t["status"] == "done")
    total = len(tasks)
    pct = round(done / total * 100) if total else 0
    text = (
        f"{T(lang, phase_key)}\n\n"
        f"📊 {done}/{total} bajarildi ({pct}%)"
    )
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
    notes_line = f"\n📝 {task['notes']}" if task.get("notes") else ""
    phase_key = PHASES.get(task["phase"], "roadmap_phase_1_3")
    status_icon = "✅ Bajarildi" if task["status"] == "done" else "⬜ Kutilmoqda"
    text = (
        f"{T(lang, phase_key)}\n\n"
        f"<b>{task['title']}</b>{notes_line}\n\n"
        f"Holat: {status_icon}"
    )
    try:
        await cb.message.edit_text(text, reply_markup=roadmap_task_kb(lang, task), parse_mode="HTML")
    except Exception:
        await cb.message.answer(text, reply_markup=roadmap_task_kb(lang, task), parse_mode="HTML")
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
    new_status = "done" if task["status"] == "pending" else "pending"
    await db.update_roadmap_task(task_id, status=new_status)
    task = await db.get_roadmap_task(task_id)
    try:
        await sheets.sync_roadmap_task(task)
    except Exception:
        pass
    await cb.answer("✅" if new_status == "done" else "⬜")
    # Refresh task view
    notes_line = f"\n📝 {task['notes']}" if task.get("notes") else ""
    phase_key = PHASES.get(task["phase"], "roadmap_phase_1_3")
    status_icon = "✅ Bajarildi" if new_status == "done" else "⬜ Kutilmoqda"
    text = (
        f"{T(lang, phase_key)}\n\n"
        f"<b>{task['title']}</b>{notes_line}\n\n"
        f"Holat: {status_icon}"
    )
    try:
        await cb.message.edit_text(text, reply_markup=roadmap_task_kb(lang, task), parse_mode="HTML")
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
    await state.clear()
    task_id = await db.create_roadmap_task(
        phase=data["phase"], title=data["title"],
        notes=notes, created_by=data.get("user_id")
    )
    task = await db.get_roadmap_task(task_id)
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
    field = parts[2]   # "title" or "notes"
    task_id = int(parts[3])
    task = await db.get_roadmap_task(task_id)
    if not task:
        await cb.answer(T(lang, "error"), show_alert=True)
        return
    await state.update_data(lang=lang, rm_task_id=task_id, rm_field=field)
    await state.set_state(RMStates.edit_value)
    ask_key = "roadmap_ask_edit_title" if field == "title" else "roadmap_ask_edit_notes"
    await cb.message.answer(T(lang, ask_key), parse_mode="HTML")
    await cb.answer()


@router.message(RMStates.edit_value)
async def rm_edit_value(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    task_id = data["rm_task_id"]
    field = data["rm_field"]
    await state.clear()
    value = "" if msg.text.strip() == "/skip" else msg.text.strip()
    await db.update_roadmap_task(task_id, **{field: value})
    task = await db.get_roadmap_task(task_id)
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
    await db.delete_roadmap_task(task_id)
    try:
        await sheets.delete_roadmap_from_sheet(task_id)
    except Exception:
        pass
    await cb.answer(T(lang, "roadmap_deleted"))
    # Go back to phase
    tasks = await db.get_roadmap_tasks(phase)
    phase_key = PHASES.get(phase, "roadmap_phase_1_3")
    done = sum(1 for t in tasks if t["status"] == "done")
    total = len(tasks)
    pct = round(done / total * 100) if total else 0
    text = f"{T(lang, phase_key)}\n\n📊 {done}/{total} bajarildi ({pct}%)"
    try:
        await cb.message.edit_text(text, reply_markup=roadmap_phase_kb(lang, tasks, phase), parse_mode="HTML")
    except Exception:
        await cb.message.answer(text, reply_markup=roadmap_phase_kb(lang, tasks, phase), parse_mode="HTML")
