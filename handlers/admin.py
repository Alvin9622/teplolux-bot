import datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from config import ADMIN_IDS, GROUP_ID
from keyboards.calendar import calendar_kb
from keyboards.kb import (
    admin_kb, task_filter_kb, tasks_list_kb, task_actions_kb, task_edit_kb,
    priority_kb, category_kb, assignee_kb, reminder_kb, month_kb,
    stats_months_kb, report_months_kb, employees_list_kb,
    user_manage_kb, by_employee_kb, back_kb,
    new_user_role_kb, new_user_lang_kb, plan_list_kb
)
from texts import T, TEXTS, status_txt, priority_txt, reminder_txt
from utils.formatters import (
    task_card, monthly_stats_text, emp_tasks_detail, employee_monthly_report,
    leaderboard_text, overdue_tasks_text
)
from utils.reminders import send_monthly_reports, safe_send

router = Router()


def is_admin(user):
    return user and (user["role"] == "admin" or user["telegram_id"] in ADMIN_IDS)


async def get_ul(tg_id):
    user = await db.get_user(tg_id)
    return user, (user["lang"] if user else "uz")


class AdminStates(StatesGroup):
    task_title    = State()
    task_desc     = State()
    task_category = State()
    task_assignee = State()
    task_deadline = State()
    task_priority = State()
    task_reminder = State()

    plan_title    = State()
    plan_desc     = State()
    plan_category = State()
    plan_month    = State()
    plan_target   = State()

    user_id       = State()
    user_name     = State()
    user_role     = State()
    user_lang     = State()

    edit_value    = State()
    edit_deadline = State()

    meeting_title = State()
    meeting_desc  = State()
    meeting_date  = State()

    plan_done     = State()


async def _cancel(msg, state, lang):
    await state.clear()
    user = await db.get_user(msg.from_user.id)
    await msg.answer(T(lang, "cancelled"))
    if user and is_admin(user):
        await msg.answer(T(lang, "admin_menu"), reply_markup=admin_kb(lang), parse_mode="HTML")


@router.message(Command("cancel"))
@router.message(Command("bekor"))
async def cmd_cancel(msg: Message, state: FSMContext):
    cur = await state.get_state()
    if not cur:
        return
    data = await state.get_data()
    await _cancel(msg, state, data.get("lang", "uz"))


@router.message(Command("admin"))
async def cmd_admin(msg: Message):
    user, lang = await get_ul(msg.from_user.id)
    if not is_admin(user):
        await msg.answer(T(lang, "no_permission"))
        return
    await msg.answer(T(lang, "admin_menu"), reply_markup=admin_kb(lang), parse_mode="HTML")


@router.callback_query(F.data == "go:admin")
async def go_admin(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    try:
        await cb.message.edit_text(T(lang, "admin_menu"), reply_markup=admin_kb(lang), parse_mode="HTML")
    except Exception:
        await cb.message.answer(T(lang, "admin_menu"), reply_markup=admin_kb(lang), parse_mode="HTML")
    await cb.answer()


# ═══════════════════════════════════════════════════════════════
# CALENDAR HELPER
# ═══════════════════════════════════════════════════════════════

async def _handle_cal(cb, state, next_state_fn):
    parts  = cb.data.split(":")
    action = parts[1]
    data   = await state.get_data()
    lang   = data.get("lang", "uz")

    if action == "ignore":
        await cb.answer()
        return
    if action == "cancel":
        await state.clear()
        if "edit_task_id" in data:
            tid = data["edit_task_id"]
            cb.data = f"task:edit:{tid}"
            await cb.answer()
            await task_edit_menu(cb)
            return
        if "edit_meeting_id" in data:
            mid = data["edit_meeting_id"]
            cb.data = f"meeting:edit:{mid}"
            await cb.answer()
            await meeting_edit(cb, state)
            return
        await cb.message.edit_text(T(lang, "cancelled"))
        await cb.answer()
        return
    if action in ("prev", "next"):
        y, m = int(parts[2]), int(parts[3])
        if action == "prev":
            m -= 1
            if m < 1: m = 12; y -= 1
        else:
            m += 1
            if m > 12: m = 1; y += 1
        await cb.message.edit_text(
            "📅 <b>Muddatni tanlang:</b>",
            reply_markup=calendar_kb(y, m), parse_mode="HTML"
        )
        await cb.answer()
        return
    if action == "day":
        y, m, d = int(parts[2]), int(parts[3]), int(parts[4])
        selected = datetime.date(y, m, d)
        await next_state_fn(cb, state, selected, lang)
        await cb.answer(selected.strftime("%d.%m.%Y"))


# ═══════════════════════════════════════════════════════════════
# VAZIFA QO'SHISH
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin:add_task")
async def add_task_start(cb: CallbackQuery, state: FSMContext):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    await state.update_data(lang=lang, creator_id=user["id"])
    await state.set_state(AdminStates.task_title)
    await cb.message.edit_text(
        T(lang, "ask_title", cancel=T(lang, "cancel_action")), parse_mode="HTML"
    )
    await cb.answer()


@router.message(AdminStates.task_title)
async def t_title(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(title=msg.text.strip())
    await state.set_state(AdminStates.task_desc)
    await msg.answer(T(data["lang"], "ask_desc", cancel=T(data["lang"], "cancel_action")), parse_mode="HTML")


@router.message(AdminStates.task_desc)
async def t_desc(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    desc = "" if msg.text.strip() == "/skip" else msg.text.strip()
    await state.update_data(desc=desc)
    await state.set_state(AdminStates.task_category)
    await msg.answer(T(lang, "ask_category", cancel=T(lang, "cancel_action")),
                     reply_markup=category_kb(lang), parse_mode="HTML")


@router.callback_query(AdminStates.task_category, F.data.startswith("category:"))
async def t_category(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    idx  = int(cb.data.split(":")[1])
    cat  = TEXTS[lang]["categories"][idx]

    # Tahrirlash rejimi
    if "edit_task_id" in data:
        task_id = data["edit_task_id"]
        await state.clear()
        await db.update_task(task_id, category=cat)
        await cb.message.edit_text(
            f"✅ Kategoriya o'zgartirildi: <b>{cat}</b>" if lang == "uz"
            else f"✅ Категория изменена: <b>{cat}</b>",
            reply_markup=back_kb(lang, f"task_view_{task_id}"),
            parse_mode="HTML"
        )
        await cb.answer()
        return

    await state.update_data(category=cat)
    await state.set_state(AdminStates.task_assignee)
    emps = await db.get_all_employees()
    await cb.message.edit_text(
        T(lang, "ask_assignee", cancel=T(lang, "cancel_action")),
        reply_markup=assignee_kb(emps), parse_mode="HTML"
    )
    await cb.answer()


@router.callback_query(AdminStates.task_assignee, F.data.startswith("assignee:"))
async def t_assignee(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    await state.update_data(assignee_id=int(cb.data.split(":")[1]))
    await state.set_state(AdminStates.task_deadline)
    now = datetime.date.today()
    await cb.message.edit_text(
        "📅 <b>Muddatni tanlang:</b>\n\n" + T(lang, "cancel_action"),
        reply_markup=calendar_kb(now.year, now.month), parse_mode="HTML"
    )
    await cb.answer()


@router.callback_query(AdminStates.task_deadline, F.data.startswith("cal:"))
async def t_deadline_cal(cb: CallbackQuery, state: FSMContext):
    async def on_day(cb, state, selected, lang):
        await state.update_data(deadline=selected.isoformat())
        await state.set_state(AdminStates.task_priority)
        dl_fmt = selected.strftime("%d.%m.%Y")
        await cb.message.edit_text(
            f"✅ Muddat: <b>{dl_fmt}</b>\n\n" + T(lang, "ask_priority", cancel=T(lang, "cancel_action")),
            reply_markup=priority_kb(lang), parse_mode="HTML"
        )
    await _handle_cal(cb, state, on_day)


@router.callback_query(AdminStates.task_priority, F.data.startswith("priority:"))
async def t_priority(cb: CallbackQuery, state: FSMContext):
    data     = await state.get_data()
    lang     = data["lang"]
    priority = cb.data.split(":")[1]

    # Tahrirlash rejimi
    if "edit_task_id" in data:
        task_id = data["edit_task_id"]
        await state.clear()
        await db.update_task(task_id, priority=priority)
        await cb.message.edit_text(
            f"✅ Ustuvorlik o'zgartirildi: <b>{priority_txt(lang, priority)}</b>" if lang == "uz"
            else f"✅ Приоритет изменён: <b>{priority_txt(lang, priority)}</b>",
            reply_markup=back_kb(lang, f"task_view_{task_id}"),
            parse_mode="HTML"
        )
        await cb.answer()
        return

    await state.update_data(priority=priority)
    await state.set_state(AdminStates.task_reminder)
    await cb.message.edit_text(
        T(lang, "ask_reminder", cancel=T(lang, "cancel_action")),
        reply_markup=reminder_kb(lang), parse_mode="HTML"
    )
    await cb.answer()


@router.callback_query(AdminStates.task_reminder, F.data.startswith("reminder:"))
async def t_reminder(cb: CallbackQuery, state: FSMContext):
    data   = await state.get_data()
    lang   = data["lang"]
    r_days = int(cb.data.split(":")[1])

    # Tahrirlash rejimi
    if "edit_task_id" in data:
        task_id = data["edit_task_id"]
        await state.clear()
        await db.update_task(task_id, reminder_days=r_days)
        await cb.message.edit_text(
            f"✅ Eslatma o'zgartirildi: <b>{reminder_txt(lang, r_days)}</b>" if lang == "uz"
            else f"✅ Напоминание изменено: <b>{reminder_txt(lang, r_days)}</b>",
            reply_markup=back_kb(lang, f"task_view_{task_id}"),
            parse_mode="HTML"
        )
        await cb.answer()
        return

    await state.clear()

    task_id  = await db.create_task(
        title=data["title"], description=data.get("desc",""),
        category=data["category"], assignee_id=data["assignee_id"],
        created_by=data["creator_id"], deadline=data["deadline"],
        priority=data["priority"], reminder_days=r_days
    )
    assignee = await db.get_user_by_id(data["assignee_id"])
    dl_fmt   = datetime.date.fromisoformat(data["deadline"]).strftime("%d.%m.%Y")
    r_txt    = reminder_txt(lang, r_days)

    if assignee:
        a_lang = assignee.get("lang") or "uz"
        notif  = T(a_lang, "notif_new_task",
                   title=data["title"], category=data["category"],
                   description=data.get("desc") or "—", deadline=dl_fmt,
                   priority=priority_txt(a_lang, data["priority"]),
                   reminder=reminder_txt(a_lang, r_days))
        confirm_kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="✅ Qabul qildim" if a_lang=="uz" else "✅ Принял",
                callback_data=f"task:confirm:{task_id}"
            )
        ]])
        try:
            await cb.bot.send_message(assignee["telegram_id"], notif,
                                      reply_markup=confirm_kb, parse_mode="HTML")
        except Exception:
            pass

    # Guruh ga xabar
    if GROUP_ID:
        group_text = (
            f"📌 <b>Yangi vazifa!</b>\n\n"
            f"📋 {data['title']}\n"
            f"👤 {assignee['full_name'] if assignee else '—'}\n"
            f"📅 {dl_fmt} | ⚡ {priority_txt('uz', data['priority'])}"
        )
        try:
            await cb.bot.send_message(GROUP_ID, group_text, parse_mode="HTML")
        except Exception:
            pass

    aname = assignee["full_name"] if assignee else "—"
    await cb.message.edit_text(
        T(lang, "task_created", title=data["title"], name=aname, deadline=dl_fmt, reminder=r_txt) +
        f"\n🆔 #{task_id}",
        reply_markup=admin_kb(lang), parse_mode="HTML"
    )
    await cb.answer("✅")


# ═══════════════════════════════════════════════════════════════
# VAZIFANI TAHRIRLASH
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("task:edit:"))
async def task_edit_menu(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    task_id = int(cb.data.split(":")[2])
    task    = await db.get_task(task_id)
    if not task:
        await cb.answer()
        return
    assignee = await db.get_user_by_id(task["assignee_id"])
    aname    = assignee["full_name"] if assignee else "—"
    text = (
        f"✏️ <b>Vazifani tahrirlash</b>\n\n"
        f"📋 {task['title']}\n"
        f"👤 {aname}\n"
        f"📅 {task.get('deadline','—')}\n\n"
        f"Nimani o'zgartirmoqchisiz?"
    )
    try:
        await cb.message.edit_text(text, reply_markup=task_edit_kb(lang, task_id), parse_mode="HTML")
    except Exception:
        await cb.message.answer(text, reply_markup=task_edit_kb(lang, task_id), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("edit:"))
async def task_edit_field(cb: CallbackQuery, state: FSMContext):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    parts   = cb.data.split(":")
    field   = parts[1]
    task_id = int(parts[2])
    task    = await db.get_task(task_id)
    if not task:
        await cb.answer()
        return

    await state.update_data(lang=lang, edit_field=field, edit_task_id=task_id)

    if field == "title":
        await state.set_state(AdminStates.edit_value)
        await cb.message.edit_text(
            f"📝 Yangi nom kiriting:\n\nHozirgi: <b>{task['title']}</b>\n\n" + T(lang, "cancel_action"),
            parse_mode="HTML"
        )
    elif field == "desc":
        await state.set_state(AdminStates.edit_value)
        await cb.message.edit_text(
            f"📄 Yangi tavsif kiriting:\n\n" + T(lang, "cancel_action"), parse_mode="HTML"
        )
    elif field == "category":
        await state.set_state(AdminStates.task_category)
        await cb.message.edit_text(
            T(lang, "ask_category", cancel=T(lang, "cancel_action")),
            reply_markup=category_kb(lang), parse_mode="HTML"
        )
    elif field == "deadline":
        await state.set_state(AdminStates.edit_deadline)
        now = datetime.date.today()
        await cb.message.edit_text(
            f"📅 <b>Yangi muddatni tanlang:</b>\n<code>tid:{task_id}</code>",
            reply_markup=calendar_kb(now.year, now.month), parse_mode="HTML"
        )
    elif field == "priority":
        await state.set_state(AdminStates.task_priority)
        await cb.message.edit_text(
            T(lang, "ask_priority", cancel=T(lang, "cancel_action")),
            reply_markup=priority_kb(lang), parse_mode="HTML"
        )
    elif field == "reminder":
        await state.set_state(AdminStates.task_reminder)
        await cb.message.edit_text(
            T(lang, "ask_reminder", cancel=T(lang, "cancel_action")),
            reply_markup=reminder_kb(lang), parse_mode="HTML"
        )
    await cb.answer()


# ═══════════════════════════════════════════════════════════════
# BARCHA VAZIFALAR
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("admin:tasks:"))
async def all_tasks(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    parts = cb.data.split(":")
    flt   = parts[2] if len(parts) > 2 else "all"
    page  = int(parts[3]) if len(parts) > 3 else 0
    tasks = await db.get_all_tasks_with_assignee(None if flt=="all" else flt)

    today = datetime.date.today().isoformat()
    done  = sum(1 for t in tasks if t["status"]=="done")
    prog  = sum(1 for t in tasks if t["status"]=="in_progress")
    over  = sum(1 for t in tasks if t.get("deadline") and t["deadline"] < today
                and t["status"] not in ("done","cancelled"))

    header = f"📋 <b>Barcha vazifalar</b> — {len(tasks)} ta\n✅{done} 🔄{prog} ⚠️{over}"
    if not tasks:
        header = T(lang, "no_tasks")
    try:
        await cb.message.edit_text(
            header,
            reply_markup=tasks_list_kb(lang, tasks, page, flt, is_admin=True),
            parse_mode="HTML"
        )
    except Exception:
        await cb.message.answer(header,
            reply_markup=tasks_list_kb(lang, tasks, page, flt, is_admin=True),
            parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "admin:task_filter")
async def task_filter(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    await cb.message.edit_text("🔽 Filter:", reply_markup=task_filter_kb(lang))
    await cb.answer()


# ═══════════════════════════════════════════════════════════════
# HODIMLAR BO'YICHA
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin:by_emp")
async def by_employee(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    emp_list = await db.get_tasks_by_assignee_grouped()
    try:
        await cb.message.edit_text(
            "👥 <b>Hodimlar bo'yicha vazifalar:</b>",
            reply_markup=by_employee_kb(lang, emp_list), parse_mode="HTML"
        )
    except Exception:
        await cb.message.answer(
            "👥 <b>Hodimlar bo'yicha vazifalar:</b>",
            reply_markup=by_employee_kb(lang, emp_list), parse_mode="HTML"
        )
    await cb.answer()


@router.callback_query(F.data.startswith("admin:emp_tasks:"))
async def emp_tasks(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    parts  = cb.data.split(":")
    emp_id = int(parts[2])
    page   = int(parts[3]) if len(parts) > 3 else 0
    emp    = await db.get_user_by_id(emp_id)
    if not emp:
        await cb.answer()
        return
    tasks  = await db.get_employee_tasks_detail(emp_id)
    text   = emp_tasks_detail(emp, tasks, lang)

    PAGE  = 8
    start = page * PAGE
    chunk = tasks[start:start+PAGE]
    rows  = []
    for t in chunk:
        icon = {"new":"🆕","in_progress":"🔄","done":"✅","cancelled":"❌","review":"👀"}.get(t["status"],"📌")
        dl   = (t.get("deadline") or "")[-5:].replace("-",".")
        rows.append([InlineKeyboardButton(
            text=f"{icon} {t['title'][:24]} {dl}",
            callback_data=f"task:view:{t['id']}"
        )])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"admin:emp_tasks:{emp_id}:{page-1}"))
    if start + PAGE < len(tasks):
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"admin:emp_tasks:{emp_id}:{page+1}"))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton(text=T(lang,"back"), callback_data="admin:by_emp")])
    try:
        await cb.message.edit_text(
            text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML"
        )
    except Exception:
        await cb.message.answer(
            text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML"
        )
    await cb.answer()


# ═══════════════════════════════════════════════════════════════
# VAZIFANI O'CHIRISH
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("task:delete:"))
async def delete_task(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    task_id = int(cb.data.split(":")[2])
    await db.delete_task(task_id)
    await cb.answer("✅ O'chirildi", show_alert=True)
    try:
        await cb.message.edit_text(
            "🗑 Vazifa o'chirildi.", reply_markup=back_kb(lang, "admin"), parse_mode="HTML"
        )
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════
# REJA QO'SHISH
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin:add_plan")
async def add_plan_start(cb: CallbackQuery, state: FSMContext):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    await state.update_data(lang=lang, creator_id=user["id"])
    await state.set_state(AdminStates.plan_title)
    await cb.message.edit_text(
        T(lang, "ask_plan_title", cancel=T(lang, "cancel_action")), parse_mode="HTML"
    )
    await cb.answer()


@router.message(AdminStates.plan_title)
async def p_title(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(title=msg.text.strip())
    await state.set_state(AdminStates.plan_desc)
    await msg.answer(T(data["lang"], "ask_plan_desc", cancel=T(data["lang"], "cancel_action")), parse_mode="HTML")


@router.message(AdminStates.plan_desc)
async def p_desc(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    desc = "" if msg.text.strip() == "/skip" else msg.text.strip()
    await state.update_data(desc=desc)
    await state.set_state(AdminStates.plan_category)
    await msg.answer(T(lang, "ask_category", cancel=T(lang, "cancel_action")),
                     reply_markup=category_kb(lang), parse_mode="HTML")


@router.callback_query(AdminStates.plan_category, F.data.startswith("category:"))
async def p_category(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    idx  = int(cb.data.split(":")[1])
    cat  = TEXTS[lang]["categories"][idx]
    await state.update_data(category=cat)
    await state.set_state(AdminStates.plan_month)
    await cb.message.edit_text(
        T(lang, "ask_month", cancel=T(lang, "cancel_action")),
        reply_markup=month_kb(lang), parse_mode="HTML"
    )
    await cb.answer()


@router.callback_query(AdminStates.plan_month, F.data.startswith("month:"))
async def p_month(cb: CallbackQuery, state: FSMContext):
    data  = await state.get_data()
    lang  = data["lang"]
    month = int(cb.data.split(":")[1])
    year  = datetime.datetime.now().year
    await state.update_data(month=month, year=year)
    await state.set_state(AdminStates.plan_target)
    await cb.message.edit_text(
        T(lang, "ask_plan_target", cancel=T(lang, "cancel_action")), parse_mode="HTML"
    )
    await cb.answer()


@router.message(AdminStates.plan_target)
async def p_target(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    try:
        target = int(msg.text.strip())
    except ValueError:
        await msg.answer(T(lang, "invalid_number"))
        return
    await state.clear()
    await db.create_plan(
        title=data["title"], description=data.get("desc",""),
        category=data["category"], month=data["month"],
        year=data["year"], target_count=target, created_by=data["creator_id"]
    )
    months = TEXTS[lang]["months"]
    await msg.answer(
        T(lang, "plan_created", title=data["title"],
          month=months[data["month"]-1], year=data["year"], target=target),
        reply_markup=admin_kb(lang), parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════════
# REJALAR RO'YHATI VA DONE_COUNT YANGILASH
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin:plans")
async def all_plans(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    now   = datetime.datetime.now()
    plans = await db.get_plans(now.month, now.year)
    months = TEXTS[lang]["months"]
    if not plans:
        await cb.message.edit_text(T(lang, "no_tasks"), reply_markup=back_kb(lang, "admin"))
        await cb.answer()
        return
    text = f"📅 <b>Rejalar — {months[now.month-1]} {now.year}</b>\n\n"
    tt = td = 0
    for p in plans:
        pct = round(p["done_count"]/p["target_count"]*100) if p["target_count"] else 0
        bar = "█"*(pct//10) + "░"*(10-pct//10)
        text += f"📌 <b>{p['title']}</b>\n📁 {p['category']}\n🎯 {p['done_count']}/{p['target_count']} [{bar}] {pct}%\n\n"
        tt += p["target_count"]
        td += p["done_count"]
    overall = round(td/tt*100) if tt else 0
    text += f"🏆 Jami: {td}/{tt} ({overall}%)"
    try:
        await cb.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✏️ Bajarilganini yangilash", callback_data="admin:update_plans")],
                [InlineKeyboardButton(text=T(lang,"back"), callback_data="go:admin")]
            ]),
            parse_mode="HTML"
        )
    except Exception:
        await cb.message.answer(text, reply_markup=back_kb(lang, "admin"), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "admin:update_plans")
async def update_plans_menu(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    now   = datetime.datetime.now()
    plans = await db.get_plans(now.month, now.year)
    try:
        await cb.message.edit_text(
            "📅 Qaysi rejaning bajarilganini yangilash?",
            reply_markup=plan_list_kb(lang, plans),
            parse_mode="HTML"
        )
    except Exception:
        await cb.message.answer(
            "📅 Qaysi rejaning bajarilganini yangilash?",
            reply_markup=plan_list_kb(lang, plans),
            parse_mode="HTML"
        )
    await cb.answer()


@router.callback_query(F.data.startswith("plan:edit:"))
async def plan_edit_done(cb: CallbackQuery, state: FSMContext):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    plan_id = int(cb.data.split(":")[2])
    await state.update_data(lang=lang, plan_id=plan_id)
    await state.set_state(AdminStates.plan_done)
    await cb.message.edit_text(
        "🎯 Bajarilgan sonini kiriting (0 dan boshlab):\n\n" + T(lang, "cancel_action"),
        parse_mode="HTML"
    )
    await cb.answer()


@router.message(AdminStates.plan_done)
async def plan_done_received(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    try:
        done = int(msg.text.strip())
    except ValueError:
        await msg.answer(T(lang, "invalid_number"))
        return
    await state.clear()
    await db.update_plan_done(data["plan_id"], done)
    await msg.answer(
        f"✅ Yangilandi! Bajarildi: {done}",
        reply_markup=back_kb(lang, "admin"), parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════════
# STATISTIKA
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin:stats")
async def stats_menu(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    try:
        await cb.message.edit_text(
            "📊 <b>Oyni tanlang:</b>",
            reply_markup=stats_months_kb(lang), parse_mode="HTML"
        )
    except Exception:
        await cb.message.answer("📊 <b>Oyni tanlang:</b>",
                                reply_markup=stats_months_kb(lang), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("stats:"))
async def show_stats(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    _, m, y  = cb.data.split(":")
    ss, us, plans = await db.get_monthly_stats(int(m), int(y))
    text = monthly_stats_text(ss, us, plans, int(m), int(y), lang)
    try:
        await cb.message.edit_text(text, reply_markup=back_kb(lang, "admin"), parse_mode="HTML")
    except Exception:
        await cb.message.answer(text, reply_markup=back_kb(lang, "admin"), parse_mode="HTML")
    await cb.answer()


# ═══════════════════════════════════════════════════════════════
# HISOBOT YUBORISH
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin:send_report")
async def send_report_menu(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    try:
        await cb.message.edit_text(
            "📨 <b>Hisobot uchun oyni tanlang:</b>",
            reply_markup=report_months_kb(lang), parse_mode="HTML"
        )
    except Exception:
        await cb.message.answer("📨 <b>Hisobot uchun oyni tanlang:</b>",
                                reply_markup=report_months_kb(lang), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("report:"))
async def send_report(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    _, m, y = cb.data.split(":")
    await cb.answer("⏳ Yuborilmoqda...")
    await send_monthly_reports(cb.bot, int(m), int(y))
    await cb.message.edit_text(
        T(lang, "report_sent"), reply_markup=back_kb(lang, "admin"), parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════════
# HODIMLAR BOSHQARUVI
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin:users")
async def users_menu(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    emps = await db.get_all_employees()
    try:
        await cb.message.edit_text(
            f"👥 <b>Hodimlar</b> — {len(emps)} kishi:",
            reply_markup=employees_list_kb(lang, emps), parse_mode="HTML"
        )
    except Exception:
        await cb.message.answer(
            f"👥 <b>Hodimlar</b> — {len(emps)} kishi:",
            reply_markup=employees_list_kb(lang, emps), parse_mode="HTML"
        )
    await cb.answer()


@router.callback_query(F.data.startswith("user:manage:"))
async def user_manage(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    emp_id = int(cb.data.split(":")[2])
    emp    = await db.get_user_by_id(emp_id)
    if not emp:
        await cb.answer()
        return
    now = datetime.datetime.now()
    _, emp_stats, _ = await db.get_monthly_stats(now.month, now.year)
    es    = next((e for e in emp_stats if e["telegram_id"]==emp["telegram_id"]), None)
    total = es["total"] if es else 0
    done  = es["done"]  if es else 0
    over  = es["overdue"] if es else 0
    pct   = round(done/total*100) if total else 0
    pos   = f"\n💼 {emp['position']}" if emp.get("position") else ""
    rl    = "👑 Admin" if emp["role"]=="admin" else "👤 Hodim"
    ll    = "O'zbekcha" if emp["lang"]=="uz" else "Русский"
    al    = "✅ Faol" if emp["is_active"] else "🚫 Bloklangan"
    text  = (
        f"👤 <b>{emp['full_name']}</b>{pos}\n"
        f"📱 @{emp['username'] or '—'} | 🎭 {rl}\n"
        f"🌐 {ll} | 🔘 {al}\n\n"
        f"📊 Bu oy: {done}/{total} ({pct}%) | ⚠️{over}"
    )
    try:
        await cb.message.edit_text(
            text, reply_markup=user_manage_kb(lang, emp_id, emp["role"]), parse_mode="HTML"
        )
    except Exception:
        await cb.message.answer(
            text, reply_markup=user_manage_kb(lang, emp_id, emp["role"]), parse_mode="HTML"
        )
    await cb.answer()


@router.callback_query(F.data.startswith("user:role:"))
async def toggle_role(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    parts    = cb.data.split(":")
    emp_id   = int(parts[2])
    new_role = parts[3]
    emp      = await db.get_user_by_id(emp_id)
    if not emp:
        await cb.answer()
        return
    await db.set_user_role(emp["telegram_id"], new_role)
    rl = "👑 Admin" if new_role=="admin" else "👤 Hodim"
    await cb.answer(f"✅ {emp['full_name']} → {rl}", show_alert=True)
    emps = await db.get_all_employees()
    await cb.message.edit_text(
        "👥 <b>Hodimlar:</b>",
        reply_markup=employees_list_kb(lang, emps), parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("user:block:"))
async def block_user(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    emp_id = int(cb.data.split(":")[2])
    emp    = await db.get_user_by_id(emp_id)
    if not emp:
        await cb.answer()
        return
    new_active = 0 if emp["is_active"] else 1
    await db.set_user_active(emp_id, new_active)
    lbl = "faollashtirildi" if new_active else "bloklandi"
    await cb.answer(f"✅ {emp['full_name']} {lbl}", show_alert=True)
    emps = await db.get_all_employees()
    await cb.message.edit_text(
        "👥 <b>Hodimlar:</b>",
        reply_markup=employees_list_kb(lang, emps), parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════════
# HODIM QO'SHISH
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin:add_user")
async def add_user_start(cb: CallbackQuery, state: FSMContext):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    await state.update_data(lang=lang)
    await state.set_state(AdminStates.user_id)
    await cb.message.edit_text(
        T(lang, "ask_new_user_id", cancel=T(lang, "cancel_action")), parse_mode="HTML"
    )
    await cb.answer()


@router.message(AdminStates.user_id)
async def au_id(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    try:
        tg_id = int(msg.text.strip())
    except ValueError:
        await msg.answer(T(lang, "invalid_number"))
        return
    existing = await db.get_user(tg_id)
    if existing:
        rl = "👑 Admin" if existing["role"]=="admin" else "👤 Hodim"
        await msg.answer(
            T(lang, "user_already_exists", name=existing["full_name"], role=rl),
            reply_markup=back_kb(lang, "admin:users"), parse_mode="HTML"
        )
        await state.clear()
        return
    await state.update_data(new_tg_id=tg_id)
    await state.set_state(AdminStates.user_name)
    await msg.answer(T(lang, "ask_new_user_name", cancel=T(lang, "cancel_action")), parse_mode="HTML")


@router.message(AdminStates.user_name)
async def au_name(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(new_name=msg.text.strip())
    await state.set_state(AdminStates.user_role)
    await msg.answer(T(data["lang"], "ask_new_user_role"), reply_markup=new_user_role_kb(data["lang"]))


@router.callback_query(AdminStates.user_role, F.data.startswith("newrole:"))
async def au_role(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.update_data(new_role=cb.data.split(":")[1])
    await state.set_state(AdminStates.user_lang)
    await cb.message.edit_text(T(data["lang"], "ask_new_user_lang"), reply_markup=new_user_lang_kb())
    await cb.answer()


@router.callback_query(AdminStates.user_lang, F.data.startswith("newlang:"))
async def au_lang(cb: CallbackQuery, state: FSMContext):
    data     = await state.get_data()
    lang     = data["lang"]
    new_lang = cb.data.split(":")[1]
    await state.clear()
    tg_id = data["new_tg_id"]
    name  = data["new_name"]
    role  = data["new_role"]
    await db.create_user(tg_id, name, None, role, new_lang, "")
    rl   = "👑 Admin" if role=="admin" else "👤 Hodim"
    ll   = "O'zbekcha" if new_lang=="uz" else "Русский"
    ok   = False
    try:
        welcome = (
            f"👋 Xush kelibsiz, {name}!\n\nTeplolux monitoring tizimiga qo'shildingiz.\n🎭 {rl}\n\n/start yuboring."
        ) if new_lang=="uz" else (
            f"👋 Добро пожаловать, {name}!\n\nВы добавлены в систему Teplolux.\n🎭 {rl}\n\n/start"
        )
        await cb.bot.send_message(tg_id, welcome, parse_mode="HTML")
        ok = True
    except Exception:
        pass
    notif = T(lang, "user_notified") if ok else T(lang, "user_not_notified")
    await cb.message.edit_text(
        T(lang, "user_added", name=name, position="—", role=rl, notif=notif),
        reply_markup=back_kb(lang, "admin:users"), parse_mode="HTML"
    )
    await cb.answer("✅")


# ═══════════════════════════════════════════════════════════════
# MAJLISLAR
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin:meetings")
async def meetings_menu(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    meetings = await db.get_meetings(15)
    rows = []
    for m in meetings[:10]:
        dl = ""
        try:
            dl = datetime.date.fromisoformat(m["meeting_date"]).strftime("%d.%m.%Y")
        except Exception:
            dl = m.get("meeting_date") or "—"
        rows.append([InlineKeyboardButton(
            text=f"📋 {m['title'][:25]} | {dl}",
            callback_data=f"meeting:view:{m['id']}"
        )])
    rows.append([InlineKeyboardButton(text="➕ Yangi majlis", callback_data="meeting:new")])
    rows.append([InlineKeyboardButton(text=T(lang,"back"), callback_data="go:admin")])
    text = f"🗓 <b>Majlislar</b> — {len(meetings)} ta:"
    try:
        await cb.message.edit_text(
            text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML"
        )
    except Exception:
        await cb.message.answer(
            text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML"
        )
    await cb.answer()


@router.callback_query(F.data == "meeting:new")
async def new_meeting(cb: CallbackQuery, state: FSMContext):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    await state.update_data(lang=lang, creator_id=user["id"])
    await state.set_state(AdminStates.meeting_title)
    await cb.message.edit_text(
        "🗓 <b>Yangi majlis</b>\n\n📝 Majlis mavzusini kiriting:\n\n" + T(lang,"cancel_action"),
        parse_mode="HTML"
    )
    await cb.answer()


@router.message(AdminStates.meeting_title)
async def m_title(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(title=msg.text.strip())
    await state.set_state(AdminStates.meeting_desc)
    await msg.answer(
        "📄 Kun tartibi / muhokama qilinadigan masalalar:\n(yoki /skip)\n\n" + T(data["lang"],"cancel_action")
    )


@router.message(AdminStates.meeting_desc)
async def m_desc(msg: Message, state: FSMContext):
    data = await state.get_data()
    desc = "" if msg.text.strip()=="/skip" else msg.text.strip()
    await state.update_data(desc=desc)
    await state.set_state(AdminStates.meeting_date)
    now = datetime.date.today()
    await msg.answer(
        "📅 <b>Majlis sanasini tanlang:</b>",
        reply_markup=calendar_kb(now.year, now.month), parse_mode="HTML"
    )


@router.callback_query(AdminStates.meeting_date, F.data.startswith("cal:"))
async def m_date_cal(cb: CallbackQuery, state: FSMContext):
    async def on_day(cb, state, selected, lang):
        data       = await state.get_data()
        await state.clear()
        dl_fmt     = selected.strftime("%d.%m.%Y")
        meeting_id = await db.create_meeting(
            title=data["title"], description=data.get("desc",""),
            meeting_date=selected.isoformat(), created_by=data["creator_id"]
        )
        # Barcha hodimga xabar
        users = await db.get_all_active_users()
        notif = f"🗓 <b>Yangi majlis!</b>\n\n📋 <b>{data['title']}</b>\n📅 {dl_fmt}"
        if data.get("desc"):
            notif += f"\n📄 {data['desc']}"
        for u in users:
            try:
                await cb.bot.send_message(u["telegram_id"], notif, parse_mode="HTML")
            except Exception:
                pass
        if GROUP_ID:
            try:
                await cb.bot.send_message(GROUP_ID, notif, parse_mode="HTML")
            except Exception:
                pass
        await cb.message.edit_text(
            f"✅ <b>Majlis yaratildi!</b>\n\n📋 {data['title']}\n📅 {dl_fmt}\n\nBarcha xabardor qilindi.\n🆔 #{meeting_id}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📋 Vazifa biriktirish", callback_data=f"meeting:tasks:{meeting_id}")],
                [InlineKeyboardButton(text=T(lang,"back"), callback_data="admin:meetings")],
            ]),
            parse_mode="HTML"
        )
    await _handle_cal(cb, state, on_day)


@router.callback_query(F.data.startswith("meeting:view:"))
async def view_meeting(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    meeting_id = int(cb.data.split(":")[2])
    meeting    = await db.get_meeting(meeting_id)
    if not meeting:
        await cb.answer("Topilmadi", show_alert=True)
        return
    tasks = await db.get_meeting_tasks(meeting_id)
    dl = ""
    try:
        dl = datetime.date.fromisoformat(meeting["meeting_date"]).strftime("%d.%m.%Y")
    except Exception:
        dl = meeting.get("meeting_date") or "—"
    text = f"🗓 <b>{meeting['title']}</b>\n📅 {dl}\n"
    if meeting.get("description"):
        text += f"📄 {meeting['description']}\n"
    if meeting.get("decisions"):
        text += f"\n✅ <b>Qarorlar:</b>\n{meeting['decisions']}\n"
    text += f"\n📋 <b>Vazifalar: {len(tasks)} ta</b>\n"
    for t in tasks:
        icon = {"new":"🆕","in_progress":"🔄","done":"✅","cancelled":"❌","review":"👀"}.get(t["status"],"📌")
        text += f"{icon} {t['title']} — {t.get('assignee_name','—')}\n"
    rows = [
        [InlineKeyboardButton(text="✏️ Tahrirlash",      callback_data=f"meeting:edit:{meeting_id}")],
        [InlineKeyboardButton(text="📊 Hisobot",          callback_data=f"meeting:report:{meeting_id}")],
        [InlineKeyboardButton(text="📋 Vazifa biriktirish",callback_data=f"meeting:tasks:{meeting_id}")],
        [InlineKeyboardButton(text="🗑 O'chirish",        callback_data=f"meeting:delete:{meeting_id}")],
        [InlineKeyboardButton(text=T(lang,"back"),        callback_data="admin:meetings")],
    ]
    try:
        await cb.message.edit_text(
            text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML"
        )
    except Exception:
        await cb.message.answer(
            text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML"
        )
    await cb.answer()


@router.callback_query(F.data.startswith("meeting:edit:"))
async def meeting_edit(cb: CallbackQuery, state: FSMContext):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    meeting_id = int(cb.data.split(":")[2])
    meeting    = await db.get_meeting(meeting_id)
    if not meeting:
        await cb.answer()
        return
    rows = [
        [InlineKeyboardButton(text="📝 Mavzuni o'zgartirish",   callback_data=f"medit:title:{meeting_id}")],
        [InlineKeyboardButton(text="📄 Kun tartibini o'zgartirish", callback_data=f"medit:desc:{meeting_id}")],
        [InlineKeyboardButton(text="✅ Qarorlar qo'shish",       callback_data=f"medit:decisions:{meeting_id}")],
        [InlineKeyboardButton(text="📅 Sanani o'zgartirish",     callback_data=f"medit:date:{meeting_id}")],
        [InlineKeyboardButton(text=T(lang,"back"),               callback_data=f"meeting:view:{meeting_id}")],
    ]
    try:
        await cb.message.edit_text(
            f"✏️ <b>{meeting['title']}</b>\n\nNimani o'zgartirish?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
            parse_mode="HTML"
        )
    except Exception:
        await cb.message.answer(
            f"✏️ <b>{meeting['title']}</b>\n\nNimani o'zgartirish?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
            parse_mode="HTML"
        )
    await cb.answer()


@router.callback_query(F.data.startswith("medit:"))
async def meeting_edit_field(cb: CallbackQuery, state: FSMContext):
    user, lang = await get_ul(cb.from_user.id)
    parts      = cb.data.split(":")
    field      = parts[1]
    meeting_id = int(parts[2])
    await state.update_data(lang=lang, edit_field=field, edit_meeting_id=meeting_id)
    if field == "date":
        await state.set_state(AdminStates.edit_deadline)
        now = datetime.date.today()
        await cb.message.edit_text(
            "📅 Yangi sanani tanlang:",
            reply_markup=calendar_kb(now.year, now.month), parse_mode="HTML"
        )
    else:
        await state.set_state(AdminStates.edit_value)
        prompts = {
            "title":     "📝 Yangi mavzuni kiriting:",
            "desc":      "📄 Yangi kun tartibini kiriting:",
            "decisions": "✅ Qabul qilingan qarorlarni kiriting:",
        }
        await cb.message.edit_text(
            prompts.get(field, "Kiriting:") + "\n\n" + T(lang, "cancel_action"),
            parse_mode="HTML"
        )
    await cb.answer()


@router.message(AdminStates.edit_value)
async def edit_value_any(msg: Message, state: FSMContext):
    data  = await state.get_data()
    lang  = data["lang"]
    field = data["edit_field"]
    await state.clear()

    if "edit_task_id" in data:
        task_id = data["edit_task_id"]
        if field == "title":
            await db.update_task(task_id, title=msg.text.strip())
        elif field == "desc":
            await db.update_task(task_id, description=msg.text.strip())
        await msg.answer("✅ O'zgartirildi!", reply_markup=back_kb(lang, f"task_view_{task_id}"), parse_mode="HTML")
    elif "edit_meeting_id" in data:
        meeting_id = data["edit_meeting_id"]
        kwargs = {}
        if field == "title":
            kwargs["title"] = msg.text.strip()
        elif field == "desc":
            kwargs["description"] = msg.text.strip()
        elif field == "decisions":
            kwargs["decisions"] = msg.text.strip()
        await db.update_meeting(meeting_id, **kwargs)
        await msg.answer("✅ O'zgartirildi!", reply_markup=back_kb(lang, f"meeting:view:{meeting_id}"), parse_mode="HTML")


@router.callback_query(AdminStates.edit_deadline, F.data.startswith("cal:"))
async def edit_deadline_any(cb: CallbackQuery, state: FSMContext):
    async def on_day(cb, state, selected, lang):
        data = await state.get_data()
        await state.clear()
        dl_fmt = selected.strftime("%d.%m.%Y")
        if "edit_task_id" in data:
            await db.update_task(data["edit_task_id"], deadline=selected.isoformat())
            await cb.message.edit_text(
                f"✅ Muddat: <b>{dl_fmt}</b>",
                reply_markup=back_kb(lang, f"task_view_{data['edit_task_id']}"),
                parse_mode="HTML"
            )
        elif "edit_meeting_id" in data:
            await db.update_meeting(data["edit_meeting_id"], meeting_date=selected.isoformat())
            await cb.message.edit_text(
                f"✅ Sana: <b>{dl_fmt}</b>",
                reply_markup=back_kb(lang, f"meeting:view:{data['edit_meeting_id']}"),
                parse_mode="HTML"
            )
    await _handle_cal(cb, state, on_day)


@router.callback_query(F.data.startswith("cal:"))
async def cal_fallback(cb: CallbackQuery, state: FSMContext):
    """State yo'qolgan hollarda (bot restart) calendar tugmalarini ushlaydi."""
    cur = await state.get_state()
    if cur is not None:
        await cb.answer()
        return

    parts  = cb.data.split(":")
    action = parts[1]

    if action == "ignore":
        await cb.answer()
        return

    if action in ("prev", "next"):
        user, lang = await get_ul(cb.from_user.id)
        y, m = int(parts[2]), int(parts[3])
        if action == "prev":
            m -= 1
            if m < 1: m = 12; y -= 1
        else:
            m += 1
            if m > 12: m = 1; y += 1
        # Extract task_id from message text if present
        import re as _re
        txt = cb.message.text or cb.message.caption or ""
        tid_match = _re.search(r'tid:(\d+)', txt)
        new_text = f"📅 <b>Yangi muddatni tanlang:</b>\n<code>tid:{tid_match.group(1)}</code>" if tid_match else "📅 <b>Muddatni tanlang:</b>"
        await cb.message.edit_text(new_text, reply_markup=calendar_kb(y, m), parse_mode="HTML")
        await cb.answer()
        return

    if action == "day" and len(parts) == 5:
        import re as _re
        txt = cb.message.text or cb.message.caption or ""
        tid_match = _re.search(r'tid:(\d+)', txt)
        if tid_match:
            user, lang = await get_ul(cb.from_user.id)
            task_id = int(tid_match.group(1))
            selected = datetime.date(int(parts[2]), int(parts[3]), int(parts[4]))
            await db.update_task(task_id, deadline=selected.isoformat())
            dl_fmt = selected.strftime("%d.%m.%Y")
            await cb.message.edit_text(
                f"✅ Muddat: <b>{dl_fmt}</b>",
                reply_markup=back_kb(lang, f"task_view_{task_id}"),
                parse_mode="HTML"
            )
            await cb.answer(dl_fmt)
            return

    if action == "cancel":
        import re as _re
        txt = cb.message.text or cb.message.caption or ""
        tid_match = _re.search(r'tid:(\d+)', txt)
        if tid_match:
            user, lang = await get_ul(cb.from_user.id)
            task_id = int(tid_match.group(1))
            cb.data = f"task:edit:{task_id}"
            await cb.answer()
            await task_edit_menu(cb)
            return

    await cb.answer("⚠️ Sessiya tugagan. Vazifani qaytadan oching.", show_alert=True)


@router.callback_query(F.data.startswith("meeting:tasks:"))
async def meeting_add_tasks(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    meeting_id = int(cb.data.split(":")[2])
    all_tasks  = await db.get_all_tasks_with_assignee()
    recent     = [t for t in all_tasks if t["status"] not in ("cancelled",)][:20]
    rows = []
    for t in recent:
        icon  = {"new":"🆕","in_progress":"🔄","done":"✅","review":"👀"}.get(t["status"],"📌")
        aname = (t.get("assignee_name") or "—")[:15]
        rows.append([InlineKeyboardButton(
            text=f"{icon} {t['title'][:25]} — {aname}",
            callback_data=f"meeting:linktask:{meeting_id}:{t['id']}"
        )])
    rows.append([InlineKeyboardButton(text=T(lang,"back"), callback_data=f"meeting:view:{meeting_id}")])
    try:
        await cb.message.edit_text(
            "📋 Vazifani tanlang:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML"
        )
    except Exception:
        await cb.message.answer(
            "📋 Vazifani tanlang:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML"
        )
    await cb.answer()


@router.callback_query(F.data.startswith("meeting:linktask:"))
async def link_task(cb: CallbackQuery):
    parts      = cb.data.split(":")
    meeting_id = int(parts[2])
    task_id    = int(parts[3])
    await db.link_task_to_meeting(meeting_id, task_id)
    await cb.answer("✅ Biriktirildi!", show_alert=True)
    cb.data = f"meeting:view:{meeting_id}"
    await view_meeting(cb)


@router.callback_query(F.data.startswith("meeting:report:"))
async def meeting_report(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    meeting_id = int(cb.data.split(":")[2])
    meeting    = await db.get_meeting(meeting_id)
    tasks      = await db.get_meeting_tasks(meeting_id)
    if not meeting:
        await cb.answer()
        return
    dl = ""
    try:
        dl = datetime.date.fromisoformat(meeting["meeting_date"]).strftime("%d.%m.%Y")
    except Exception:
        dl = "—"
    total = len(tasks)
    done  = sum(1 for t in tasks if t["status"]=="done")
    prog  = sum(1 for t in tasks if t["status"]=="in_progress")
    canc  = sum(1 for t in tasks if t["status"]=="cancelled")
    pct   = round(done/total*100) if total else 0
    from utils.formatters import progress_bar
    text = (
        f"📊 <b>Majlis hisoboti</b>\n"
        f"📋 {meeting['title']}\n"
        f"📅 {dl}\n"
        f"{'—'*22}\n\n"
        f"📌 Jami: {total} | ✅ {done} | 🔄 {prog} | ❌ {canc}\n"
        f"🎯 {pct}%\n{progress_bar(pct)}\n\n"
        f"<b>Vazifalar holati:</b>\n"
    )
    for t in tasks:
        icon = {"new":"🆕","in_progress":"🔄","done":"✅","cancelled":"❌","review":"👀"}.get(t["status"],"📌")
        aname = t.get("assignee_name") or "—"
        line  = f"{icon} {t['title']} — {aname}"
        if t["status"]=="cancelled" and t.get("cancel_reason"):
            line += f"\n   💬 {t['cancel_reason']}"
        text += line + "\n"
    try:
        await cb.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=T(lang,"back"), callback_data=f"meeting:view:{meeting_id}")]
            ]),
            parse_mode="HTML"
        )
    except Exception:
        await cb.message.answer(text, reply_markup=back_kb(lang, "admin:meetings"), parse_mode="HTML")
    await cb.answer()


# ═══════════════════════════════════════════════════════════════
# REYTING (LEADERBOARD)
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin:leaderboard")
async def show_leaderboard(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    emp_list = await db.get_all_time_leaderboard()
    text     = leaderboard_text(emp_list, lang)
    try:
        await cb.message.edit_text(
            text,
            reply_markup=back_kb(lang, "admin"),
            parse_mode="HTML"
        )
    except Exception:
        await cb.message.answer(text, reply_markup=back_kb(lang, "admin"), parse_mode="HTML")
    await cb.answer()


# ═══════════════════════════════════════════════════════════════
# KECHIKKAN VAZIFALAR
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "admin:overdue")
async def show_overdue(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    tasks = await db.get_overdue_tasks_admin()
    if not tasks:
        txt = "✅ Kechikkan vazifa yo'q!" if lang == "uz" else "✅ Просроченных задач нет!"
        try:
            await cb.message.edit_text(txt, reply_markup=back_kb(lang, "admin"), parse_mode="HTML")
        except Exception:
            await cb.message.answer(txt, reply_markup=back_kb(lang, "admin"), parse_mode="HTML")
        await cb.answer()
        return

    text = overdue_tasks_text(tasks, lang)
    PAGE = 5
    rows = []
    for t in tasks[:PAGE]:
        aname = (t.get("assignee_name") or "—")[:16]
        rows.append([InlineKeyboardButton(
            text=f"🔴 {t['title'][:24]} — {aname}",
            callback_data=f"task:view:{t['id']}"
        )])
    rows.append([InlineKeyboardButton(text=T(lang, "back"), callback_data="go:admin")])
    try:
        await cb.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
            parse_mode="HTML"
        )
    except Exception:
        await cb.message.answer(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
            parse_mode="HTML"
        )
    await cb.answer()


# ═══════════════════════════════════════════════════════════════
# EXCEL EKSPORT
# ═══════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("admin:export:"))
async def export_menu(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    rows = []
    now = datetime.datetime.now()
    months = TEXTS[lang]["months"]
    for i in range(3, -1, -1):
        d = (now.replace(day=1) - datetime.timedelta(days=i * 28)).replace(day=1)
        rows.append([InlineKeyboardButton(
            text=f"📥 {months[d.month-1]} {d.year}",
            callback_data=f"admin:do_export:{d.month}:{d.year}"
        )])
    rows.append([InlineKeyboardButton(
        text="📥 Barcha vazifalar" if lang == "uz" else "📥 Все задачи",
        callback_data="admin:do_export:0:0"
    )])
    rows.append([InlineKeyboardButton(text=T(lang, "back"), callback_data="go:admin")])
    try:
        await cb.message.edit_text(
            "📥 <b>Excel eksport — oyni tanlang:</b>" if lang == "uz"
            else "📥 <b>Экспорт Excel — выберите период:</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
            parse_mode="HTML"
        )
    except Exception:
        await cb.message.answer(
            "📥 <b>Excel eksport:</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
            parse_mode="HTML"
        )
    await cb.answer()


@router.callback_query(F.data.startswith("admin:do_export:"))
async def do_export(cb: CallbackQuery):
    from aiogram.types import BufferedInputFile
    from utils.excel_export import build_tasks_excel
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    await cb.answer("⏳ Tayyorlanmoqda..." if lang == "uz" else "⏳ Готовится...", show_alert=False)

    parts = cb.data.split(":")
    month = int(parts[3])
    year  = int(parts[4])

    tasks = await db.get_all_tasks_for_export(month or None, year or None)
    if not tasks:
        await cb.message.answer("📭 Vazifa topilmadi." if lang == "uz" else "📭 Задачи не найдены.")
        return

    buf = build_tasks_excel(tasks, month or None, year or None)
    now = datetime.datetime.now()
    if month:
        months = TEXTS[lang]["months"]
        fname  = f"teplolux_{months[month-1].lower()}_{year}.xlsx"
    else:
        fname = f"teplolux_all_{now.strftime('%Y%m%d')}.xlsx"

    doc = BufferedInputFile(buf.read(), filename=fname)
    caption = (
        f"📊 <b>Excel hisobot</b>\n📋 {len(tasks)} ta vazifa\n📅 {now.strftime('%d.%m.%Y %H:%M')}"
        if lang == "uz" else
        f"📊 <b>Excel отчёт</b>\n📋 {len(tasks)} задач\n📅 {now.strftime('%d.%m.%Y %H:%M')}"
    )
    await cb.message.answer_document(doc, caption=caption, parse_mode="HTML")


@router.callback_query(F.data.startswith("meeting:delete:"))
async def delete_meeting(cb: CallbackQuery):
    user, lang = await get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer()
        return
    meeting_id = int(cb.data.split(":")[2])
    await db.delete_meeting(meeting_id)
    await cb.answer("✅ O'chirildi", show_alert=True)
    cb.data = "admin:meetings"
    await meetings_menu(cb)
