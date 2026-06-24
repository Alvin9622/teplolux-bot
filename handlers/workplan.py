"""Ish rejalari: shablonlar, hodimga tayinlash, bajarish jarayoni."""
import datetime
import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

import database as db
from keyboards.kb import (
    wp_admin_menu_kb, wp_templates_kb, wp_template_view_kb, wp_period_kb,
    wp_plan_kb, wp_item_kb, wp_my_plans_kb, wp_all_plans_kb, assignee_kb, back_kb
)
from texts import T, TEXTS

logger = logging.getLogger(__name__)
router = Router()

MONTHS_UZ = ["Yanvar","Fevral","Mart","Aprel","May","Iyun",
              "Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr"]


class WPStates(StatesGroup):
    tmpl_title    = State()
    tmpl_position = State()
    tmpl_period   = State()
    tmpl_items    = State()   # loop
    assign_month  = State()
    item_count    = State()
    item_note     = State()


def _plan_progress(items):
    if not items:
        return 0
    total = sum(i["target_count"] for i in items)
    done  = sum(i["done_count"]   for i in items)
    return round(done / total * 100) if total else 0


def _progress_bar(pct, width=8):
    filled = round(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)


def _plan_text(plan, items, lang):
    pct  = _plan_progress(items)
    bar  = _progress_bar(pct)
    month_name = MONTHS_UZ[plan["month"] - 1] if lang == "uz" else \
                 TEXTS["ru"]["months"][plan["month"] - 1]
    lines = [
        f"📋 <b>{plan['title']}</b>",
        f"👤 {plan.get('assignee_name') or '—'}",
        f"📅 {month_name} {plan['year']}",
        f"📊 {bar} {pct}%\n",
    ]
    for item in items:
        done_pct = round(item["done_count"] / item["target_count"] * 100) if item["target_count"] else 0
        icon = "✅" if done_pct >= 100 else ("🔄" if done_pct > 0 else "⬜")
        lines.append(f"{icon} {item['title']}: <b>{item['done_count']}/{item['target_count']}</b> {item['unit']}")
        if item.get("notes"):
            lines.append(f"   💬 {item['notes']}")
    return "\n".join(lines)


# ─── ADMIN MENU ──────────────────────────────────────────────────

@router.callback_query(F.data == "go:wp_menu")
async def wp_menu(cb: CallbackQuery):
    user = await db.get_user(cb.from_user.id)
    if not user or user["role"] != "admin":
        await cb.answer("Ruxsat yo'q", show_alert=True); return
    lang = user["lang"]
    await cb.message.edit_text(
        T(lang, "wp_menu_title"),
        reply_markup=wp_admin_menu_kb(lang),
        parse_mode="HTML",
    )
    await cb.answer()


# ─── TEMPLATES ───────────────────────────────────────────────────

@router.callback_query(F.data.in_({"wp:templates", "go:wp_templates"}))
async def wp_templates(cb: CallbackQuery):
    user = await db.get_user(cb.from_user.id)
    if not user or user["role"] != "admin":
        await cb.answer(); return
    lang = user["lang"]
    templates = await db.get_wp_templates()
    if not templates:
        await cb.message.edit_text(
            T(lang, "wp_no_templates"),
            reply_markup=back_kb(lang, "wp_menu"),
            parse_mode="HTML",
        )
    else:
        await cb.message.edit_text(
            T(lang, "wp_templates_title"),
            reply_markup=wp_templates_kb(lang, templates),
            parse_mode="HTML",
        )
    await cb.answer()


@router.callback_query(F.data.startswith("wp:tmpl:"))
async def wp_template_view(cb: CallbackQuery):
    tmpl_id = int(cb.data.split(":")[2])
    user    = await db.get_user(cb.from_user.id)
    if not user or user["role"] != "admin":
        await cb.answer(); return
    lang     = user["lang"]
    template = await db.get_wp_template(tmpl_id)
    items    = await db.get_wp_template_items(tmpl_id)
    if not template:
        await cb.answer("Topilmadi", show_alert=True); return
    period = T(lang, "wp_period_monthly") if template["period_type"] == "monthly" else T(lang, "wp_period_weekly")
    text = (
        f"📋 <b>{template['title']}</b>\n"
        f"💼 {template['position']}\n"
        f"📅 {period}\n\n"
        f"<b>Bandlar:</b>\n"
    )
    for i, item in enumerate(items, 1):
        text += f"{i}. {item['title']} — {item['target_count']} {item['unit']}\n"
    await cb.message.edit_text(text, reply_markup=wp_template_view_kb(lang, tmpl_id), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("wp:del_tmpl:"))
async def wp_delete_template(cb: CallbackQuery):
    tmpl_id = int(cb.data.split(":")[2])
    user    = await db.get_user(cb.from_user.id)
    if not user or user["role"] != "admin":
        await cb.answer(); return
    await db.delete_wp_template(tmpl_id)
    await cb.answer("✅ O'chirildi")
    await wp_templates(cb)


# ─── NEW TEMPLATE FSM ────────────────────────────────────────────

@router.callback_query(F.data == "wp:new_template")
async def wp_new_template(cb: CallbackQuery, state: FSMContext):
    user = await db.get_user(cb.from_user.id)
    if not user or user["role"] != "admin":
        await cb.answer(); return
    lang = user["lang"]
    await state.set_state(WPStates.tmpl_title)
    await state.update_data(lang=lang, items=[])
    await cb.message.edit_text(T(lang, "wp_ask_title"), parse_mode="HTML",
                                reply_markup=back_kb(lang, "wp_templates"))
    await cb.answer()


@router.message(WPStates.tmpl_title)
async def wp_tmpl_title(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(title=message.text.strip())
    await state.set_state(WPStates.tmpl_position)
    await message.answer(T(lang, "wp_ask_position"), parse_mode="HTML")


@router.message(WPStates.tmpl_position)
async def wp_tmpl_position(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(position=message.text.strip())
    await state.set_state(WPStates.tmpl_period)
    await message.answer(T(lang, "wp_ask_period"), reply_markup=wp_period_kb(lang), parse_mode="HTML")


@router.callback_query(F.data.startswith("wp_period:"))
async def wp_tmpl_period(cb: CallbackQuery, state: FSMContext):
    period = cb.data.split(":")[1]
    data   = await state.get_data()
    lang   = data.get("lang", "uz")
    await state.update_data(period_type=period)
    await state.set_state(WPStates.tmpl_items)
    await cb.message.edit_text(T(lang, "wp_ask_item_title"), parse_mode="HTML")
    await cb.answer()


@router.message(WPStates.tmpl_items)
async def wp_tmpl_add_item(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    if message.text and message.text.strip() == "/done":
        # Shablon saqlash
        items = data.get("items", [])
        if not items:
            await message.answer("⚠️ Kamida 1 band kiritish kerak!")
            return
        tmpl_id = await db.create_wp_template(
            title=data["title"], position=data["position"],
            period_type=data["period_type"], created_by=message.from_user.id
        )
        for i, item in enumerate(items):
            await db.add_wp_template_item(tmpl_id, item["title"], item["target"], item["unit"], i)
        await state.clear()
        await message.answer(T(lang, "wp_template_saved"), parse_mode="HTML",
                              reply_markup=wp_template_view_kb(lang, tmpl_id))
        return

    # Item title saqlash, keyin miqdor so'rash
    await state.update_data(_current_item_title=message.text.strip())
    await message.answer(T(lang, "wp_ask_item_target"))


# target count kiritish — items state ichida
@router.message(WPStates.tmpl_items, F.text.regexp(r"^\d+$"))
async def wp_tmpl_item_target(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    current_title = data.get("_current_item_title")
    if not current_title:
        await message.answer(T(lang, "wp_ask_item_title"))
        return
    await state.update_data(_current_target=int(message.text.strip()), _current_item_title=None)
    await message.answer(T(lang, "wp_ask_item_unit"))


# Boshqa text — unit yoki yangi item title
# Bu logika oddiyroq: faqat ketma-ket title → target → unit olamiz
# Lekin FSM state da bu murakkab, shuning uchun oddiy yondashuv ishlatamiz:
# Har bir xabar formatini tekshiramiz


# ─── ASSIGN PLAN ─────────────────────────────────────────────────

@router.callback_query(F.data.startswith("wp:assign:"))
async def wp_assign_start(cb: CallbackQuery, state: FSMContext):
    tmpl_id = int(cb.data.split(":")[2])
    user    = await db.get_user(cb.from_user.id)
    if not user or user["role"] != "admin":
        await cb.answer(); return
    lang = user["lang"]
    employees = await db.get_all_employees()
    if not employees:
        await cb.answer("Hodim yo'q", show_alert=True); return
    await state.set_state(WPStates.assign_month)
    await state.update_data(tmpl_id=tmpl_id, lang=lang)
    await cb.message.edit_text(
        T(lang, "wp_assign_title"),
        reply_markup=assignee_kb(employees),
        parse_mode="HTML",
    )
    await cb.answer()


@router.callback_query(WPStates.assign_month, F.data.startswith("assignee:"))
async def wp_assign_employee(cb: CallbackQuery, state: FSMContext):
    emp_id = int(cb.data.split(":")[1])
    data   = await state.get_data()
    lang   = data.get("lang", "uz")
    await state.update_data(emp_id=emp_id)
    await cb.message.edit_text(T(lang, "wp_ask_month"), parse_mode="HTML")
    await cb.answer()


@router.message(WPStates.assign_month)
async def wp_assign_month(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    try:
        month = int(message.text.strip())
        if not 1 <= month <= 12:
            raise ValueError
    except ValueError:
        await message.answer("❌ 1-12 oralig'ida son kiriting")
        return

    now      = datetime.datetime.now()
    year     = now.year if month >= now.month else now.year + 1
    tmpl_id  = data["tmpl_id"]
    emp_id   = data["emp_id"]
    template = await db.get_wp_template(tmpl_id)
    t_items  = await db.get_wp_template_items(tmpl_id)

    plan_id = await db.create_work_plan(
        user_id=emp_id, template_id=tmpl_id,
        title=template["title"], period_type=template["period_type"],
        month=month, year=year, week_num=0,
        created_by=message.from_user.id
    )
    for i, item in enumerate(t_items):
        await db.add_work_plan_item(plan_id, item["title"], item["target_count"], item["unit"], i)

    await state.clear()
    emp = await db.get_user_by_id(emp_id)
    month_name = MONTHS_UZ[month - 1] if lang == "uz" else TEXTS["ru"]["months"][month - 1]
    await message.answer(
        f"✅ {template['title']} — {emp['full_name']} ga {month_name} {year} uchun tayinlandi!",
        parse_mode="HTML"
    )
    # Hodimga xabar
    try:
        emp_lang = emp.get("lang", "uz")
        await message.bot.send_message(
            emp["telegram_id"],
            f"📋 <b>Yangi ish rejasi tayinlandi!</b>\n"
            f"📌 {template['title']}\n"
            f"📅 {month_name} {year}\n\n"
            f"Ko'rish uchun: /start → Mening rejam",
            parse_mode="HTML"
        )
    except Exception:
        pass


# ─── ALL PLANS (ADMIN) ───────────────────────────────────────────

@router.callback_query(F.data.in_({"wp:all_plans", "go:wp_all_plans"}))
async def wp_all_plans(cb: CallbackQuery):
    user = await db.get_user(cb.from_user.id)
    if not user or user["role"] != "admin":
        await cb.answer(); return
    lang  = user["lang"]
    now   = datetime.datetime.now()
    plans = await db.get_work_plans(month=now.month, year=now.year)
    for p in plans:
        items = await db.get_work_plan_items(p["id"])
        p["items_total"] = sum(i["target_count"] for i in items)
        p["items_done"]  = sum(i["done_count"]   for i in items)
    if not plans:
        await cb.message.edit_text(
            "📭 Bu oy uchun hech kimga reja tayinlanmagan.",
            reply_markup=back_kb(lang, "wp_menu"),
        )
    else:
        await cb.message.edit_text(
            f"📋 <b>{now.month}/{now.year} — Barcha rejalar</b>",
            reply_markup=wp_all_plans_kb(lang, plans),
            parse_mode="HTML",
        )
    await cb.answer()


# ─── PLAN VIEW ───────────────────────────────────────────────────

@router.callback_query(F.data.startswith("wp:plan:"))
async def wp_plan_view(cb: CallbackQuery):
    plan_id = int(cb.data.split(":")[2])
    user    = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(); return
    lang     = user["lang"]
    is_admin = user["role"] == "admin"
    plan     = await db.get_work_plan(plan_id)
    if not plan:
        await cb.answer("Topilmadi", show_alert=True); return
    if not is_admin and plan["user_id"] != user["id"]:
        await cb.answer("Ruxsat yo'q", show_alert=True); return
    items = await db.get_work_plan_items(plan_id)
    await cb.message.edit_text(
        _plan_text(plan, items, lang),
        reply_markup=wp_plan_kb(lang, plan_id, items, is_admin=is_admin),
        parse_mode="HTML",
    )
    await cb.answer()


# ─── MY PLAN (EMPLOYEE) ──────────────────────────────────────────

@router.callback_query(F.data.in_({"go:myplan", "wp:myplans"}))
async def wp_my_plans(cb: CallbackQuery):
    user = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(); return
    lang  = user["lang"]
    now   = datetime.datetime.now()
    plans = await db.get_work_plans(user_id=user["id"], month=now.month, year=now.year)
    if not plans:
        await cb.message.edit_text(
            T(lang, "wp_my_plan_empty"),
            reply_markup=back_kb(lang, "main"),
            parse_mode="HTML",
        )
        await cb.answer(); return
    # Bir oy uchun bitta plan bo'lsa to'g'ridan ko'rsat
    if len(plans) == 1:
        cb.data = f"wp:plan:{plans[0]['id']}"
        await wp_plan_view(cb)
        return
    for p in plans:
        items = await db.get_work_plan_items(p["id"])
        p["items_total"] = sum(i["target_count"] for i in items)
        p["items_done"]  = sum(i["done_count"]   for i in items)
    await cb.message.edit_text(
        T(lang, "btn_my_workplan"),
        reply_markup=wp_my_plans_kb(lang, plans),
        parse_mode="HTML",
    )
    await cb.answer()


# ─── ITEM UPDATE ─────────────────────────────────────────────────

@router.callback_query(F.data.startswith("wp:item:"))
async def wp_item_view(cb: CallbackQuery):
    item_id = int(cb.data.split(":")[2])
    user    = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(); return
    lang     = user["lang"]
    is_admin = user["role"] == "admin"
    item     = await db.get_work_plan_item(item_id)
    if not item:
        await cb.answer("Topilmadi", show_alert=True); return
    pct  = round(item["done_count"] / item["target_count"] * 100) if item["target_count"] else 0
    bar  = _progress_bar(pct)
    text = (
        f"📌 <b>{item['title']}</b>\n"
        f"🎯 Maqsad: {item['target_count']} {item['unit']}\n"
        f"✅ Bajarildi: {item['done_count']} {item['unit']}\n"
        f"📊 {bar} {pct}%"
    )
    if item.get("notes"):
        text += f"\n💬 {item['notes']}"
    await cb.message.edit_text(
        text,
        reply_markup=wp_item_kb(lang, item_id, item["plan_id"], is_admin=is_admin),
        parse_mode="HTML",
    )
    await cb.answer()


@router.callback_query(F.data.startswith("wp:update:"))
async def wp_item_update_start(cb: CallbackQuery, state: FSMContext):
    item_id = int(cb.data.split(":")[2])
    user    = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(); return
    lang = user["lang"]
    item = await db.get_work_plan_item(item_id)
    if not item:
        await cb.answer("Topilmadi", show_alert=True); return
    await state.set_state(WPStates.item_count)
    await state.update_data(item_id=item_id, lang=lang)
    prompt = T(lang, "wp_ask_done_count").format(target=item["target_count"])
    await cb.message.answer(prompt, parse_mode="HTML", reply_markup=back_kb(lang, f"wp_plan_{item['plan_id']}"))
    await cb.answer()


@router.message(WPStates.item_count)
async def wp_item_count_save(message: Message, state: FSMContext):
    data    = await state.get_data()
    lang    = data.get("lang", "uz")
    item_id = data.get("item_id")
    try:
        count = int(message.text.strip())
        if count < 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Musbat son kiriting")
        return
    item = await db.get_work_plan_item(item_id)
    count = min(count, item["target_count"])
    new_status = "done" if count >= item["target_count"] else ("pending" if count == 0 else "partial")
    await db.update_work_plan_item(item_id, done_count=count, status=new_status)
    await state.clear()
    await message.answer(
        T(lang, "wp_item_done").format(done=count, target=item["target_count"], unit=item["unit"]),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("wp:note:"))
async def wp_item_note_start(cb: CallbackQuery, state: FSMContext):
    item_id = int(cb.data.split(":")[2])
    user    = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(); return
    lang = user["lang"]
    await state.set_state(WPStates.item_note)
    await state.update_data(item_id=item_id, lang=lang)
    await cb.message.answer("💬 Izoh yozing:", reply_markup=back_kb(lang, "myplan"))
    await cb.answer()


@router.message(WPStates.item_note)
async def wp_item_note_save(message: Message, state: FSMContext):
    data    = await state.get_data()
    item_id = data.get("item_id")
    lang    = data.get("lang", "uz")
    await db.update_work_plan_item(item_id, notes=message.text.strip())
    await state.clear()
    await message.answer("✅ Izoh saqlandi!", parse_mode="HTML")
