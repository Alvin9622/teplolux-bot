"""KPI tizimi: maqsadlar belgilash, natijalarni kiritish, hisobot."""
import datetime
import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

import database as db
from keyboards.kb import (
    kpi_admin_menu_kb, kpi_emp_kb, kpi_view_kb, kpi_my_months_kb, back_kb
)
from texts import T, TEXTS

logger = logging.getLogger(__name__)
router = Router()

MONTHS_UZ = ["Yanvar","Fevral","Mart","Aprel","May","Iyun",
              "Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr"]


class KPIStates(StatesGroup):
    metric_name   = State()
    metric_target = State()
    metric_unit   = State()
    update_actual = State()


def _get_months(n=4):
    now    = datetime.datetime.now()
    result = []
    for i in range(n):
        m = (now.month - i - 1) % 12 + 1
        y = now.year if (now.month - i) > 0 else now.year - 1
        result.append({"month": m, "year": y,
                        "label": f"{MONTHS_UZ[m-1]} {y}"})
    return result


def _kpi_text(targets, user_name, month, year, lang):
    month_name = MONTHS_UZ[month - 1] if lang == "uz" else TEXTS["ru"]["months"][month - 1]
    lines = [f"📊 <b>KPI — {user_name}</b>", f"📅 {month_name} {year}\n"]
    total_pct = []
    for t in targets:
        pct  = round(t["actual_value"] / t["target_value"] * 100) if t["target_value"] else 0
        total_pct.append(pct)
        bar  = "█" * round(pct / 100 * 8) + "░" * (8 - round(pct / 100 * 8))
        icon = "✅" if pct >= 100 else ("🔄" if pct > 0 else "⬜")
        lines.append(
            f"{icon} <b>{t['metric_name']}</b>\n"
            f"   {bar} {pct}%\n"
            f"   📌 {t['actual_value']} / {t['target_value']} {t['unit']}"
        )
        if t.get("note"):
            lines.append(f"   💬 {t['note']}")
        lines.append("")
    if total_pct:
        avg = round(sum(total_pct) / len(total_pct))
        lines.append(f"━━━━━━━━━━━━━━━━")
        lines.append(f"🏆 Umumiy: <b>{avg}%</b>")
    return "\n".join(lines)


# ─── ADMIN MENU ──────────────────────────────────────────────────

@router.callback_query(F.data.in_({"go:kpi_menu", "kpi:menu"}))
async def kpi_menu(cb: CallbackQuery):
    user = await db.get_user(cb.from_user.id)
    if not user or user["role"] != "admin":
        await cb.answer("Ruxsat yo'q", show_alert=True); return
    lang      = user["lang"]
    employees = await db.get_all_employees()
    await cb.message.edit_text(
        T(lang, "kpi_menu_title"),
        reply_markup=kpi_admin_menu_kb(lang, employees),
        parse_mode="HTML",
    )
    await cb.answer()


@router.callback_query(F.data.startswith("kpi:emp:"))
async def kpi_emp_view(cb: CallbackQuery):
    emp_id = int(cb.data.split(":")[2])
    user   = await db.get_user(cb.from_user.id)
    if not user or user["role"] != "admin":
        await cb.answer(); return
    lang   = user["lang"]
    emp    = await db.get_user_by_id(emp_id)
    months = _get_months()
    await cb.message.edit_text(
        f"👤 <b>{emp['full_name']}</b>\n📊 KPI ko'rish yoki belgilash:",
        reply_markup=kpi_emp_kb(lang, emp_id, months),
        parse_mode="HTML",
    )
    await cb.answer()


@router.callback_query(F.data.startswith("kpi:view:"))
async def kpi_view(cb: CallbackQuery):
    parts  = cb.data.split(":")
    emp_id = int(parts[2])
    month  = int(parts[3])
    year   = int(parts[4])
    user   = await db.get_user(cb.from_user.id)
    if not user or user["role"] != "admin":
        await cb.answer(); return
    lang    = user["lang"]
    emp     = await db.get_user_by_id(emp_id)
    targets = await db.get_kpi_targets(user_id=emp_id, month=month, year=year)
    if not targets:
        await cb.message.edit_text(
            f"📊 {emp['full_name']} — {MONTHS_UZ[month-1]} {year}\n\n{T(lang, 'kpi_no_targets')}",
            reply_markup=kpi_view_kb(lang, [], emp_id, month, year, is_admin=True),
            parse_mode="HTML",
        )
    else:
        await cb.message.edit_text(
            _kpi_text(targets, emp["full_name"], month, year, lang),
            reply_markup=kpi_view_kb(lang, targets, emp_id, month, year, is_admin=True),
            parse_mode="HTML",
        )
    await cb.answer()


@router.callback_query(F.data.startswith("kpi:clear:"))
async def kpi_clear(cb: CallbackQuery):
    parts  = cb.data.split(":")
    emp_id = int(parts[2])
    month  = int(parts[3])
    year   = int(parts[4])
    user   = await db.get_user(cb.from_user.id)
    if not user or user["role"] != "admin":
        await cb.answer(); return
    targets = await db.get_kpi_targets(user_id=emp_id, month=month, year=year)
    for t in targets:
        await db.delete_kpi_target(t["id"])
    await cb.answer("✅ Tozalandi")
    cb.data = f"kpi:view:{emp_id}:{month}:{year}"
    await kpi_view(cb)


# ─── SET KPI (FSM) ───────────────────────────────────────────────

@router.callback_query(F.data.startswith("kpi:set:"))
async def kpi_set_start(cb: CallbackQuery, state: FSMContext):
    emp_id = int(cb.data.split(":")[2])
    user   = await db.get_user(cb.from_user.id)
    if not user or user["role"] != "admin":
        await cb.answer(); return
    lang = user["lang"]
    now  = datetime.datetime.now()
    await state.set_state(KPIStates.metric_name)
    await state.update_data(emp_id=emp_id, lang=lang,
                             month=now.month, year=now.year, metrics=[])
    await cb.message.answer(T(lang, "kpi_ask_metric"), parse_mode="HTML",
                             reply_markup=back_kb(lang, "kpi_menu"))
    await cb.answer()


@router.message(KPIStates.metric_name)
async def kpi_metric_name(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    if message.text.strip() == "/done":
        metrics = data.get("metrics", [])
        if not metrics:
            await message.answer("⚠️ Kamida 1 ko'rsatkich kiriting!")
            return
        emp_id = data["emp_id"]
        month  = data["month"]
        year   = data["year"]
        for m in metrics:
            await db.create_kpi_target(
                user_id=emp_id, month=month, year=year,
                metric_name=m["name"], target_value=m["target"],
                unit=m["unit"], created_by=message.from_user.id
            )
        await state.clear()
        emp = await db.get_user_by_id(emp_id)
        await message.answer(T(lang, "kpi_saved"), parse_mode="HTML")
        # Hodimga xabar
        try:
            await message.bot.send_message(
                emp["telegram_id"],
                f"📊 <b>{MONTHS_UZ[month-1]} {year} uchun KPI belgilandi!</b>\n"
                + "\n".join(f"• {m['name']}: {m['target']} {m['unit']}" for m in metrics),
                parse_mode="HTML"
            )
        except Exception:
            pass
        return
    await state.update_data(_cur_metric=message.text.strip())
    await state.set_state(KPIStates.metric_target)
    await message.answer(T(lang, "kpi_ask_target"), parse_mode="HTML")


@router.message(KPIStates.metric_target)
async def kpi_metric_target(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    try:
        target = float(message.text.strip().replace(",", "."))
    except ValueError:
        await message.answer("❌ Son kiriting")
        return
    await state.update_data(_cur_target=target)
    await state.set_state(KPIStates.metric_unit)
    await message.answer(T(lang, "kpi_ask_unit"), parse_mode="HTML")


@router.message(KPIStates.metric_unit)
async def kpi_metric_unit(message: Message, state: FSMContext):
    data   = await state.get_data()
    lang   = data.get("lang", "uz")
    unit   = "" if message.text.strip() == "/skip" else message.text.strip()
    metrics = data.get("metrics", [])
    metrics.append({
        "name":   data["_cur_metric"],
        "target": data["_cur_target"],
        "unit":   unit,
    })
    await state.update_data(metrics=metrics, _cur_metric=None, _cur_target=None)
    await state.set_state(KPIStates.metric_name)
    added = len(metrics)
    await message.answer(
        f"{T(lang, 'kpi_metric_added')}\n"
        f"<i>Qo'shildi: {added} ta. /done — saqlash</i>",
        parse_mode="HTML"
    )


# ─── UPDATE ACTUAL (EMPLOYEE) ────────────────────────────────────

@router.callback_query(F.data.startswith("kpi:upd:"))
async def kpi_update_start(cb: CallbackQuery, state: FSMContext):
    kpi_id = int(cb.data.split(":")[2])
    user   = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(); return
    lang   = user["lang"]
    target = await db.get_kpi_target(kpi_id)
    if not target:
        await cb.answer("Topilmadi", show_alert=True); return
    await state.set_state(KPIStates.update_actual)
    await state.update_data(kpi_id=kpi_id, lang=lang)
    await cb.message.answer(
        T(lang, "kpi_ask_actual").format(unit=target["unit"] or ""),
        parse_mode="HTML",
        reply_markup=back_kb(lang, "mykpi"),
    )
    await cb.answer()


@router.message(KPIStates.update_actual)
async def kpi_update_save(message: Message, state: FSMContext):
    data   = await state.get_data()
    lang   = data.get("lang", "uz")
    kpi_id = data.get("kpi_id")
    try:
        actual = float(message.text.strip().replace(",", "."))
    except ValueError:
        await message.answer("❌ Son kiriting")
        return
    target = await db.get_kpi_target(kpi_id)
    await db.update_kpi_target(kpi_id, actual_value=actual)
    await state.clear()
    pct = round(actual / target["target_value"] * 100) if target["target_value"] else 0
    await message.answer(
        T(lang, "kpi_updated").format(
            actual=actual, target=target["target_value"],
            unit=target["unit"] or "", pct=pct
        ),
        parse_mode="HTML",
    )


# ─── MY KPI (EMPLOYEE) ───────────────────────────────────────────

@router.callback_query(F.data.in_({"go:mykpi", "kpi:mylist"}))
async def kpi_my_list(cb: CallbackQuery):
    user = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(); return
    lang   = user["lang"]
    months = _get_months(3)
    await cb.message.edit_text(
        T(lang, "kpi_my_title"),
        reply_markup=kpi_my_months_kb(lang, months),
        parse_mode="HTML",
    )
    await cb.answer()


@router.callback_query(F.data.startswith("kpi:myview:"))
async def kpi_my_view(cb: CallbackQuery):
    parts = cb.data.split(":")
    month = int(parts[2])
    year  = int(parts[3])
    user  = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(); return
    lang    = user["lang"]
    targets = await db.get_kpi_targets(user_id=user["id"], month=month, year=year)
    if not targets:
        await cb.message.edit_text(
            T(lang, "kpi_no_targets"),
            reply_markup=back_kb(lang, "mykpi"),
            parse_mode="HTML",
        )
    else:
        await cb.message.edit_text(
            _kpi_text(targets, user["full_name"], month, year, lang),
            reply_markup=kpi_view_kb(lang, targets, user["id"], month, year, is_admin=False),
            parse_mode="HTML",
        )
    await cb.answer()
