import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
import utils.sheets as sheets
from config import ADMIN_IDS, GROUP_ID
from keyboards.kb import expense_menu_kb, expense_view_kb, currency_kb, back_kb
from texts import T

router = Router()

STATUS_ICONS = {
    "pending":   "⏳",
    "approved":  "✅",
    "rejected":  "❌",
    "postponed": "🔄",
    "paid":      "💳",
}


class ExpStates(StatesGroup):
    name      = State()
    amount    = State()
    currency  = State()
    deadline  = State()
    note      = State()
    file      = State()
    reject    = State()
    postpone  = State()


def is_admin(user):
    return user and (user["role"] == "admin" or user["telegram_id"] in ADMIN_IDS)


async def _get_ul(tg_id):
    user = await db.get_user(tg_id)
    return user, (user["lang"] if user else "uz")


def _exp_card(exp, creator=None, approver=None, lang="uz"):
    status_icon = STATUS_ICONS.get(exp["status"], "❓")
    status_key = f"exp_status_{exp['status']}"
    lines = [
        f"💰 <b>{exp['name']}</b>",
        f"💵 {exp['amount']} {exp['currency']}",
    ]
    if exp.get("deadline"):
        lines.append(f"📅 Muddat: {exp['deadline']}")
    if exp.get("note"):
        lines.append(f"💬 {exp['note']}")
    lines.append(f"Holat: {status_icon} {T(lang, status_key)}")
    if creator:
        lines.append(f"👤 Yaratgan: {creator['full_name']}")
    if approver:
        lines.append(f"✅ Tasdiqlagan: {approver['full_name']}")
    if exp.get("reject_reason"):
        lines.append(f"❌ Sabab: {exp['reject_reason']}")
    if exp.get("postpone_date"):
        lines.append(f"🔄 Yangi muddat: {exp['postpone_date']}")
    lines.append(f"\n🆔 #{exp['id']} | {exp['created_at'][:10]}")
    return "\n".join(lines)


async def _notify_creator(bot, exp, lang_key, **kwargs):
    creator = await db.get_user_by_id(exp["created_by"])
    if not creator:
        return
    lang = creator.get("lang", "uz")
    text = T(lang, lang_key, name=exp["name"], amount=exp["amount"],
             currency=exp["currency"], **kwargs)
    try:
        await bot.send_message(creator["telegram_id"], text, parse_mode="HTML")
    except Exception:
        pass


# ─── MENU ────────────────────────────────────────────────────────

@router.callback_query(F.data == "go:expenses")
@router.callback_query(F.data == "admin:expenses")
async def expenses_menu(cb: CallbackQuery):
    user, lang = await _get_ul(cb.from_user.id)
    if not user:
        await cb.answer(T("uz", "not_registered"), show_alert=True)
        return
    admin = is_admin(user)
    pending_count = len(await db.get_expenses(status="pending")) if admin else 0
    text = T(lang, "expense_menu")
    if admin and pending_count:
        text += f"\n\n⏳ <b>{pending_count} ta xarajat tasdiqlash kutmoqda</b>"
    try:
        await cb.message.edit_text(text, reply_markup=expense_menu_kb(lang, admin), parse_mode="HTML")
    except Exception:
        await cb.message.answer(text, reply_markup=expense_menu_kb(lang, admin), parse_mode="HTML")
    await cb.answer()


# ─── ADD EXPENSE FSM ─────────────────────────────────────────────

@router.callback_query(F.data == "exp:add")
async def exp_add_start(cb: CallbackQuery, state: FSMContext):
    user, lang = await _get_ul(cb.from_user.id)
    if not user:
        await cb.answer(T("uz", "not_registered"), show_alert=True)
        return
    await state.update_data(lang=lang, user_db_id=user["id"])
    await state.set_state(ExpStates.name)
    await cb.message.answer(T(lang, "expense_ask_name", cancel=T(lang, "cancel_action")), parse_mode="HTML")
    await cb.answer()


@router.message(ExpStates.name)
async def exp_name(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    await state.update_data(exp_name=msg.text.strip())
    await state.set_state(ExpStates.amount)
    await msg.answer(T(lang, "expense_ask_amount", cancel=T(lang, "cancel_action")), parse_mode="HTML")


@router.message(ExpStates.amount)
async def exp_amount(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    try:
        amount = float(msg.text.strip().replace(",", ".").replace(" ", ""))
    except ValueError:
        await msg.answer(T(lang, "expense_invalid_amount"))
        return
    await state.update_data(exp_amount=amount)
    await state.set_state(ExpStates.currency)
    await msg.answer(T(lang, "expense_ask_currency"), reply_markup=currency_kb(), parse_mode="HTML")


@router.callback_query(ExpStates.currency, F.data.startswith("expcur:"))
async def exp_currency(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    currency = cb.data.split(":")[1]
    await state.update_data(exp_currency=currency)
    await state.set_state(ExpStates.deadline)
    await cb.message.answer(T(lang, "expense_ask_deadline", cancel=T(lang, "cancel_action")), parse_mode="HTML")
    await cb.answer()


@router.message(ExpStates.deadline)
async def exp_deadline(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    text = msg.text.strip()
    deadline = ""
    if text != "/skip":
        try:
            parts = text.split(".")
            deadline = f"{parts[2]}-{parts[1]}-{parts[0]}"
            datetime.date.fromisoformat(deadline)
            deadline = text  # keep original format for display
        except Exception:
            await msg.answer(T(lang, "invalid_date"))
            return
    await state.update_data(exp_deadline=deadline)
    await state.set_state(ExpStates.note)
    await msg.answer(T(lang, "expense_ask_note", cancel=T(lang, "cancel_action")), parse_mode="HTML")


@router.message(ExpStates.note)
async def exp_note(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    note = "" if msg.text.strip() == "/skip" else msg.text.strip()
    await state.update_data(exp_note=note)
    await state.set_state(ExpStates.file)
    await msg.answer(T(lang, "expense_ask_file", cancel=T(lang, "cancel_action")), parse_mode="HTML")


@router.message(ExpStates.file, F.photo | F.document)
async def exp_file(msg: Message, state: FSMContext):
    data = await state.get_data()
    if msg.photo:
        file_id, file_type = msg.photo[-1].file_id, "photo"
    else:
        file_id, file_type = msg.document.file_id, "document"
    await state.update_data(exp_file_id=file_id, exp_file_type=file_type)
    await _save_expense(msg, state)


@router.message(ExpStates.file, F.text)
async def exp_file_skip(msg: Message, state: FSMContext):
    if msg.text.strip() == "/skip":
        await state.update_data(exp_file_id="", exp_file_type="")
        await _save_expense(msg, state)
    else:
        data = await state.get_data()
        await msg.answer(T(data["lang"], "expense_ask_file", cancel=T(data["lang"], "cancel_action")), parse_mode="HTML")


async def _save_expense(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    lang = data["lang"]
    expense_id = await db.create_expense(
        name=data["exp_name"], amount=data["exp_amount"],
        currency=data.get("exp_currency", "USD"),
        deadline=data.get("exp_deadline", ""),
        note=data.get("exp_note", ""),
        file_id=data.get("exp_file_id", ""),
        file_type=data.get("exp_file_type", ""),
        created_by=data["user_db_id"],
    )
    exp = await db.get_expense(expense_id)
    creator = await db.get_user_by_id(data["user_db_id"])

    # Sync to sheets
    try:
        await sheets.sync_expense(exp, creator)
    except Exception:
        pass

    # Activity log
    try:
        await db.log_activity_db("expense", expense_id, "created",
                                 data["user_db_id"], "", data["exp_name"])
    except Exception:
        pass

    # Budget alert check
    try:
        from handlers.budget import check_budget_alert
        await check_budget_alert(msg.bot, exp, lang)
    except Exception:
        pass

    # Notify admins
    admin_notif = T("uz", "expense_notif_admin",
                    name=exp["name"], amount=exp["amount"], currency=exp["currency"],
                    deadline=exp.get("deadline") or "—",
                    author=creator["full_name"] if creator else "?",
                    note=exp.get("note") or "—")
    approve_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Tasdiqlash",  callback_data=f"exp:approve:{expense_id}"),
        InlineKeyboardButton(text="❌ Rad etish",   callback_data=f"exp:reject:{expense_id}"),
    ], [
        InlineKeyboardButton(text="🔄 Kechiktirish", callback_data=f"exp:postpone:{expense_id}"),
    ]])
    # Faqat adminlarga yuboriladi — guruhga EMAS
    for admin_id in ADMIN_IDS:
        try:
            await msg.bot.send_message(admin_id, admin_notif, reply_markup=approve_kb, parse_mode="HTML")
            if exp.get("file_id"):
                ft = exp.get("file_type", "document")
                if ft == "photo":
                    await msg.bot.send_photo(admin_id, exp["file_id"])
                else:
                    await msg.bot.send_document(admin_id, exp["file_id"])
        except Exception:
            pass

    await msg.answer(
        T(lang, "expense_submitted", name=exp["name"], amount=exp["amount"], currency=exp["currency"]),
        reply_markup=back_kb(lang, "expenses"),
        parse_mode="HTML"
    )


# ─── VIEW EXPENSE ─────────────────────────────────────────────────

@router.callback_query(F.data.startswith("exp:view:"))
async def exp_view(cb: CallbackQuery):
    user, lang = await _get_ul(cb.from_user.id)
    if not user:
        await cb.answer()
        return
    exp_id = int(cb.data.split(":")[2])
    exp = await db.get_expense(exp_id)
    if not exp:
        await cb.answer(T(lang, "error"), show_alert=True)
        return
    creator  = await db.get_user_by_id(exp["created_by"])
    approver = await db.get_user_by_id(exp["approved_by"]) if exp.get("approved_by") else None
    admin = is_admin(user)
    if not admin and exp["created_by"] != user["id"]:
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    text = _exp_card(exp, creator, approver, lang)
    kb = expense_view_kb(lang, exp_id, exp["status"], admin)
    try:
        await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await cb.message.answer(text, reply_markup=kb, parse_mode="HTML")
    # Send file separately if exists
    if exp.get("file_id"):
        try:
            ft = exp.get("file_type", "document")
            if ft == "photo":
                await cb.message.answer_photo(exp["file_id"])
            else:
                await cb.message.answer_document(exp["file_id"])
        except Exception:
            pass
    await cb.answer()


# ─── LIST EXPENSES ────────────────────────────────────────────────

async def _show_expense_list(cb: CallbackQuery, expenses, lang: str, title: str):
    if not expenses:
        await cb.answer(T(lang, "expense_none"), show_alert=True)
        return
    rows = []
    for e in expenses:
        icon = STATUS_ICONS.get(e["status"], "❓")
        rows.append([InlineKeyboardButton(
            text=f"{icon} {e['name'][:25]} — {e['amount']} {e['currency']}",
            callback_data=f"exp:view:{e['id']}"
        )])
    rows.append([InlineKeyboardButton(text=T(lang, "back"), callback_data="go:expenses")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    try:
        await cb.message.edit_text(f"<b>{title}</b>", reply_markup=kb, parse_mode="HTML")
    except Exception:
        await cb.message.answer(f"<b>{title}</b>", reply_markup=kb, parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "exp:my")
async def exp_my(cb: CallbackQuery):
    user, lang = await _get_ul(cb.from_user.id)
    if not user:
        await cb.answer()
        return
    expenses = await db.get_expenses(created_by=user["id"])
    await _show_expense_list(cb, expenses, lang, T(lang, "expense_my"))


@router.callback_query(F.data == "exp:pending")
async def exp_pending(cb: CallbackQuery):
    user, lang = await _get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    expenses = await db.get_expenses(status="pending")
    await _show_expense_list(cb, expenses, lang, T(lang, "expense_pending_list"))


@router.callback_query(F.data == "exp:all")
async def exp_all(cb: CallbackQuery):
    user, lang = await _get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    expenses = await db.get_expenses()
    await _show_expense_list(cb, expenses, lang, T(lang, "expense_all"))


# ─── APPROVE ─────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("exp:approve:"))
async def exp_approve(cb: CallbackQuery):
    user, lang = await _get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    exp_id = int(cb.data.split(":")[2])
    exp = await db.get_expense(exp_id)
    if not exp:
        await cb.answer(T(lang, "error"), show_alert=True)
        return
    await db.update_expense(exp_id, status="approved", approved_by=user["id"])
    exp = await db.get_expense(exp_id)
    creator = await db.get_user_by_id(exp["created_by"])
    try:
        await sheets.sync_expense(exp, creator, user)
    except Exception:
        pass
    try:
        await db.log_activity_db("expense", exp_id, "approved",
                                 user["id"], "pending", "approved")
    except Exception:
        pass
    await _notify_creator(cb.bot, exp, "expense_approved_msg",
                          amount=exp["amount"], currency=exp["currency"])
    await cb.answer("✅ Tasdiqlandi!", show_alert=True)
    try:
        await cb.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass


# ─── REJECT ──────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("exp:reject:"))
async def exp_reject_start(cb: CallbackQuery, state: FSMContext):
    user, lang = await _get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    exp_id = int(cb.data.split(":")[2])
    await state.update_data(lang=lang, exp_id=exp_id, approver_id=user["id"])
    await state.set_state(ExpStates.reject)
    await cb.message.answer(T(lang, "expense_ask_reject"), parse_mode="HTML")
    await cb.answer()


@router.message(ExpStates.reject)
async def exp_reject_reason(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    lang   = data["lang"]
    exp_id = data["exp_id"]
    reason = msg.text.strip()
    await db.update_expense(exp_id, status="rejected",
                            approved_by=data["approver_id"], reject_reason=reason)
    exp = await db.get_expense(exp_id)
    creator = await db.get_user_by_id(exp["created_by"])
    approver = await db.get_user_by_id(data["approver_id"])
    try:
        await sheets.sync_expense(exp, creator, approver)
    except Exception:
        pass
    try:
        await db.log_activity_db("expense", exp_id, "rejected",
                                 data["approver_id"], "pending", f"rejected: {reason}")
    except Exception:
        pass
    await _notify_creator(msg.bot, exp, "expense_rejected_msg", reason=reason)
    await msg.answer(T(lang, "saved"), parse_mode="HTML")


# ─── POSTPONE ────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("exp:postpone:"))
async def exp_postpone_start(cb: CallbackQuery, state: FSMContext):
    user, lang = await _get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    exp_id = int(cb.data.split(":")[2])
    await state.update_data(lang=lang, exp_id=exp_id, approver_id=user["id"])
    await state.set_state(ExpStates.postpone)
    await cb.message.answer(T(lang, "expense_ask_postpone"), parse_mode="HTML")
    await cb.answer()


@router.message(ExpStates.postpone)
async def exp_postpone_date(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    lang     = data["lang"]
    exp_id   = data["exp_id"]
    new_date = msg.text.strip()
    await db.update_expense(exp_id, status="postponed",
                            approved_by=data["approver_id"], postpone_date=new_date)
    exp = await db.get_expense(exp_id)
    creator  = await db.get_user_by_id(exp["created_by"])
    approver = await db.get_user_by_id(data["approver_id"])
    try:
        await sheets.sync_expense(exp, creator, approver)
    except Exception:
        pass
    try:
        await db.log_activity_db("expense", exp_id, "postponed",
                                 data["approver_id"], "pending", f"postponed to {new_date}")
    except Exception:
        pass
    await _notify_creator(msg.bot, exp, "expense_postponed_msg", date=new_date)
    await msg.answer(T(lang, "saved"), parse_mode="HTML")


# ─── MARK PAID ───────────────────────────────────────────────────

@router.callback_query(F.data.startswith("exp:paid:"))
async def exp_paid(cb: CallbackQuery):
    user, lang = await _get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    exp_id = int(cb.data.split(":")[2])
    await db.update_expense(exp_id, status="paid", approved_by=user["id"])
    exp = await db.get_expense(exp_id)
    creator = await db.get_user_by_id(exp["created_by"])
    try:
        await sheets.sync_expense(exp, creator, user)
    except Exception:
        pass
    try:
        await db.log_activity_db("expense", exp_id, "paid",
                                 user["id"], "approved", "paid")
    except Exception:
        pass
    await cb.answer(T(lang, "exp_status_paid"), show_alert=True)
    try:
        await cb.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass


# ─── EXPENSE STATS ───────────────────────────────────────────────

@router.callback_query(F.data == "exp:stats")
async def exp_stats(cb: CallbackQuery):
    user, lang = await _get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    now = datetime.datetime.now()
    month, year = now.month, now.year
    stats = await db.get_expense_stats(month, year)

    months_uz = ["Yanvar","Fevral","Mart","Aprel","May","Iyun",
                 "Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr"]
    months_ru = ["Январь","Февраль","Март","Апрель","Май","Июнь",
                 "Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"]
    month_name = months_uz[month-1] if lang == "uz" else months_ru[month-1]
    prev_month_name = (months_uz if lang == "uz" else months_ru)[stats["prev_month"]-1]

    sc = stats["status_counts"]
    ct = stats["currency_totals"]
    pt = stats["prev_totals"]

    lines = [T(lang, "exp_stats_title"), f"📅 {month_name} {year}\n"]

    if lang == "uz":
        lines.append("📊 <b>Holat bo'yicha:</b>")
        lines.append(f"  ⏳ Kutilmoqda: {sc.get('pending', 0)}")
        lines.append(f"  ✅ Tasdiqlangan: {sc.get('approved', 0)}")
        lines.append(f"  ❌ Rad etilgan: {sc.get('rejected', 0)}")
        lines.append(f"  🔄 Kechiktirilgan: {sc.get('postponed', 0)}")
        lines.append(f"  💳 To'langan: {sc.get('paid', 0)}")
        lines.append("\n💰 <b>Tasdiqlangan + To'langan summa:</b>")
    else:
        lines.append("📊 <b>По статусам:</b>")
        lines.append(f"  ⏳ Ожидает: {sc.get('pending', 0)}")
        lines.append(f"  ✅ Подтверждено: {sc.get('approved', 0)}")
        lines.append(f"  ❌ Отклонено: {sc.get('rejected', 0)}")
        lines.append(f"  🔄 Отложено: {sc.get('postponed', 0)}")
        lines.append(f"  💳 Оплачено: {sc.get('paid', 0)}")
        lines.append("\n💰 <b>Подтверждено + Оплачено:</b>")

    for currency in ("USD", "UZS", "RUB"):
        cur_total = ct.get(currency, 0)
        prev_total = pt.get(currency, 0)
        diff = cur_total - prev_total
        diff_str = f"+{diff:,.0f}" if diff >= 0 else f"{diff:,.0f}"
        lines.append(f"  {currency}: {cur_total:,.0f} ({diff_str} vs {prev_month_name})")

    if stats["top3"]:
        top_label = "🏆 <b>Top 3 xarajat:</b>" if lang == "uz" else "🏆 <b>Топ 3 расходов:</b>"
        lines.append(f"\n{top_label}")
        for i, item in enumerate(stats["top3"], 1):
            lines.append(f"  {i}. {item['name'][:30]} — {item['total']:,.0f}")

    text = "\n".join(lines)
    from keyboards.kb import back_kb as bk
    try:
        await cb.message.edit_text(text, reply_markup=bk(lang, "expenses"), parse_mode="HTML")
    except Exception:
        await cb.message.answer(text, reply_markup=bk(lang, "expenses"), parse_mode="HTML")
    await cb.answer()


