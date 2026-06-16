import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery

import database as db
from config import ADMIN_IDS
from keyboards.kb import dashboard_kb
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
    return "█" * filled + "░" * (width - filled) + f" {done}/{total} ({round(done/total*100)}%)"


PHASE_LABELS = {
    "1-3":   "1–3 oy",
    "4-6":   "4–6 oy",
    "7-9":   "7–9 oy",
    "10-18": "10–18 oy",
}


async def _build_admin_dashboard(lang):
    data = await db.get_dashboard_data_admin()
    now = datetime.datetime.now()
    month, year = now.month, now.year
    months_uz = ["Yanvar","Fevral","Mart","Aprel","May","Iyun",
                 "Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr"]
    months_ru = ["Январь","Февраль","Март","Апрель","Май","Июнь",
                 "Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"]
    month_name = months_uz[month-1] if lang == "uz" else months_ru[month-1]

    lines = [T(lang, "dashboard_title"), f"📅 {month_name} {year}\n"]

    if lang == "uz":
        lines.append(f"⏳ Kutilayotgan vazifalar: <b>{data['pending_tasks']}</b>")
        lines.append(f"🔴 Kechikkan yo'l xarita: <b>{data['overdue_tasks']}</b>")
        lines.append(f"💰 Kutilayotgan xarajatlar: <b>{data['pending_expenses']}</b>")
        lines.append("\n🗺 <b>Yo'l xarita jarayoni:</b>")
    else:
        lines.append(f"⏳ Задач ожидает: <b>{data['pending_tasks']}</b>")
        lines.append(f"🔴 Просроченных (карта): <b>{data['overdue_tasks']}</b>")
        lines.append(f"💰 Расходов ожидает: <b>{data['pending_expenses']}</b>")
        lines.append("\n🗺 <b>Прогресс дорожной карты:</b>")

    total_done = 0
    total_all = 0
    for phase, pp in data["phase_progress"].items():
        d, t = pp["done"], pp["total"]
        total_done += d
        total_all += t
        label = PHASE_LABELS.get(phase, phase)
        bar = _progress_bar(d, t)
        lines.append(f"  {label}: {bar}")

    overall = _progress_bar(total_done, total_all)
    lbl = "Umumiy" if lang == "uz" else "Итого"
    lines.append(f"\n{lbl}: {overall}")

    # Budget summary
    budget = await db.get_budget(month, year)
    if budget:
        lines.append("\n💰 <b>Byudjet / Бюджет:</b>" if lang == "uz" else "\n💰 <b>Бюджет:</b>")
        for currency, limit_key in [("USD", "limit_usd"), ("UZS", "limit_uzs"), ("RUB", "limit_rub")]:
            limit = budget.get(limit_key) or 0
            if limit > 0:
                spent = await db.get_monthly_expense_total(month, year, currency)
                pct = round(spent / limit * 100) if limit else 0
                lines.append(f"  {currency}: {spent:,.0f}/{limit:,.0f} ({pct}%)")

    return "\n".join(lines)


async def _build_employee_dashboard(user, lang):
    data = await db.get_dashboard_data_employee(user["id"])
    task_counts = data["task_counts"]
    exp_counts = data["exp_counts"]

    lines = [T(lang, "dashboard_title"), ""]

    if lang == "uz":
        lines.append("📋 <b>Mening vazifalarim:</b>")
        lines.append(f"  🆕 Yangi: {task_counts.get('new', 0)}")
        lines.append(f"  🔄 Jarayonda: {task_counts.get('in_progress', 0)}")
        lines.append(f"  👀 Tekshiruvda: {task_counts.get('review', 0)}")
        lines.append(f"  ✅ Bajarildi: {task_counts.get('done', 0)}")
        lines.append(f"  ❌ Bekor: {task_counts.get('cancelled', 0)}")
        lines.append("\n💰 <b>Mening xarajatlarim:</b>")
        lines.append(f"  ⏳ Kutilmoqda: {exp_counts.get('pending', 0)}")
        lines.append(f"  ✅ Tasdiqlangan: {exp_counts.get('approved', 0)}")
        lines.append(f"  💳 To'langan: {exp_counts.get('paid', 0)}")
        lines.append(f"  ❌ Rad etilgan: {exp_counts.get('rejected', 0)}")
    else:
        lines.append("📋 <b>Мои задачи:</b>")
        lines.append(f"  🆕 Новые: {task_counts.get('new', 0)}")
        lines.append(f"  🔄 В процессе: {task_counts.get('in_progress', 0)}")
        lines.append(f"  👀 На проверке: {task_counts.get('review', 0)}")
        lines.append(f"  ✅ Выполнено: {task_counts.get('done', 0)}")
        lines.append(f"  ❌ Отменено: {task_counts.get('cancelled', 0)}")
        lines.append("\n💰 <b>Мои расходы:</b>")
        lines.append(f"  ⏳ Ожидают: {exp_counts.get('pending', 0)}")
        lines.append(f"  ✅ Подтверждено: {exp_counts.get('approved', 0)}")
        lines.append(f"  💳 Оплачено: {exp_counts.get('paid', 0)}")
        lines.append(f"  ❌ Отклонено: {exp_counts.get('rejected', 0)}")

    return "\n".join(lines)


@router.callback_query(F.data.in_({"go:dashboard", "dashboard:refresh"}))
async def dashboard(cb: CallbackQuery):
    user, lang = await _get_ul(cb.from_user.id)
    if not user:
        await cb.answer(T("uz", "not_registered"), show_alert=True)
        return

    if is_admin(user):
        text = await _build_admin_dashboard(lang)
    else:
        text = await _build_employee_dashboard(user, lang)

    kb = dashboard_kb(lang)
    try:
        await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await cb.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await cb.answer()
