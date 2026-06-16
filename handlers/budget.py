import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from config import ADMIN_IDS
from keyboards.kb import budget_menu_kb, back_kb
from texts import T

router = Router()


def is_admin(user):
    return user and (user["role"] == "admin" or user["telegram_id"] in ADMIN_IDS)


async def _get_ul(tg_id):
    user = await db.get_user(tg_id)
    return user, (user["lang"] if user else "uz")


def _progress_bar(done, total, width=10):
    if total == 0:
        return "░" * width + " 0/0"
    filled = round(done / total * width)
    filled = max(0, min(width, filled))
    return "█" * filled + "░" * (width - filled) + f" {done:,.0f} / {total:,.0f} ({round(done/total*100)}%)"


class BudgetStates(StatesGroup):
    usd_limit = State()
    uzs_limit = State()
    rub_limit = State()


@router.callback_query(F.data == "budget:menu")
async def budget_menu(cb: CallbackQuery):
    user, lang = await _get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    now = datetime.datetime.now()
    month, year = now.month, now.year
    budget = await db.get_budget(month, year)
    lines = [T(lang, "budget_menu"), ""]
    months_uz = ["Yanvar","Fevral","Mart","Aprel","May","Iyun",
                 "Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr"]
    months_ru = ["Январь","Февраль","Март","Апрель","Май","Июнь",
                 "Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"]
    month_name = months_uz[month-1] if lang == "uz" else months_ru[month-1]
    lines.append(f"📅 <b>{month_name} {year}</b>\n")

    for currency, limit_key in [("USD", "limit_usd"), ("UZS", "limit_uzs"), ("RUB", "limit_rub")]:
        spent = await db.get_monthly_expense_total(month, year, currency)
        limit = (budget[limit_key] if budget else 0) or 0
        if limit > 0:
            bar = _progress_bar(spent, limit)
            lines.append(f"<b>{currency}:</b> {bar}")
        else:
            lines.append(f"<b>{currency}:</b> {spent:,.0f} / ♾ (no limit)")

    text = "\n".join(lines)
    try:
        await cb.message.edit_text(text, reply_markup=budget_menu_kb(lang), parse_mode="HTML")
    except Exception:
        await cb.message.answer(text, reply_markup=budget_menu_kb(lang), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "budget:set")
async def budget_set_start(cb: CallbackQuery, state: FSMContext):
    user, lang = await _get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    now = datetime.datetime.now()
    await state.update_data(lang=lang, month=now.month, year=now.year)
    await state.set_state(BudgetStates.usd_limit)
    await cb.message.answer(T(lang, "budget_ask_usd"), parse_mode="HTML")
    await cb.answer()


@router.message(BudgetStates.usd_limit)
async def budget_usd(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    try:
        val = float(msg.text.strip().replace(",", ".").replace(" ", ""))
    except ValueError:
        await msg.answer(T(lang, "invalid_number"))
        return
    await state.update_data(limit_usd=val)
    await state.set_state(BudgetStates.uzs_limit)
    await msg.answer(T(lang, "budget_ask_uzs"), parse_mode="HTML")


@router.message(BudgetStates.uzs_limit)
async def budget_uzs(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    try:
        val = float(msg.text.strip().replace(",", ".").replace(" ", ""))
    except ValueError:
        await msg.answer(T(lang, "invalid_number"))
        return
    await state.update_data(limit_uzs=val)
    await state.set_state(BudgetStates.rub_limit)
    await msg.answer(T(lang, "budget_ask_rub"), parse_mode="HTML")


@router.message(BudgetStates.rub_limit)
async def budget_rub(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    try:
        val = float(msg.text.strip().replace(",", ".").replace(" ", ""))
    except ValueError:
        await msg.answer(T(lang, "invalid_number"))
        return
    await state.clear()
    await db.set_budget(
        month=data["month"], year=data["year"],
        limit_usd=data["limit_usd"], limit_uzs=data["limit_uzs"], limit_rub=val
    )
    await msg.answer(T(lang, "budget_saved"), reply_markup=back_kb(lang, "admin"), parse_mode="HTML")


async def check_budget_alert(bot, expense, lang="uz"):
    """Called after saving an expense. Alerts admins if 80%/100% threshold crossed."""
    now = datetime.datetime.now()
    month, year = now.month, now.year
    currency = expense.get("currency", "USD")
    budget = await db.get_budget(month, year)
    if not budget:
        return
    limit_map = {"USD": "limit_usd", "UZS": "limit_uzs", "RUB": "limit_rub"}
    limit_key = limit_map.get(currency)
    if not limit_key:
        return
    limit = budget.get(limit_key) or 0
    if limit <= 0:
        return
    spent = await db.get_monthly_expense_total(month, year, currency)
    pct = spent / limit * 100
    if pct >= 100:
        text = T(lang, "budget_alert_100",
                 currency=currency, spent=f"{spent:,.2f}", limit=f"{limit:,.2f}")
    elif pct >= 80:
        text = T(lang, "budget_alert_80",
                 currency=currency, spent=f"{spent:,.2f}", limit=f"{limit:,.2f}")
    else:
        return
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text, parse_mode="HTML")
        except Exception:
            pass
