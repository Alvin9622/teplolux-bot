import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

import database as db
from config import ADMIN_IDS
from keyboards.kb import back_kb
from texts import T

router = Router()


def is_admin(user):
    return user and (user["role"] == "admin" or user["telegram_id"] in ADMIN_IDS)


def _confirm_kb(task_id, lang):
    label = "Qabul qildim" if lang == "uz" else "Принял задание"
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ " + label, callback_data=f"task:confirm:{task_id}")
    ]])


def _fmt(iso):
    try:
        return datetime.date.fromisoformat(iso).strftime("%d.%m.%Y")
    except Exception:
        return iso or "—"


@router.callback_query(F.data.startswith("task:confirm:"))
async def confirm_task(cb: CallbackQuery):
    task_id = int(cb.data.split(":")[2])
    user    = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer()
        return
    lang = user["lang"]
    task = await db.get_task(task_id)
    if not task:
        await cb.answer("Topilmadi", show_alert=True)
        return
    if task["assignee_id"] != user["id"]:
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    if task.get("confirmed_at"):
        msg = "Allaqachon tasdiqlangan!" if lang=="uz" else "Уже подтверждено!"
        await cb.answer(msg, show_alert=True)
        return
    await db.confirm_task(task_id, user["id"])
    text = (
        f"✅ Vazifa qabul qilindi!\n\n📋 {task['title']}\n/mytasks"
    ) if lang=="uz" else (
        f"✅ Задача принята!\n\n📋 {task['title']}\n/mytasks"
    )
    try:
        await cb.message.edit_text(text, parse_mode="HTML")
    except Exception:
        await cb.message.answer(text, parse_mode="HTML")
    for aid in ADMIN_IDS:
        try:
            await cb.bot.send_message(
                aid,
                f"✅ <b>Vazifa qabul qilindi!</b>\n\n📋 {task['title']}\n👤 {user['full_name']}",
                parse_mode="HTML"
            )
        except Exception:
            pass
    await cb.answer("✅")


@router.callback_query(F.data == "admin:unconfirmed")
async def unconfirmed_tasks(cb: CallbackQuery):
    user = await db.get_user(cb.from_user.id)
    if not user or not is_admin(user):
        await cb.answer()
        return
    lang  = user["lang"]
    tasks = await db.get_unconfirmed_tasks_admin()
    if not tasks:
        text = "✅ Barcha vazifalar tasdiqlangan!" if lang=="uz" else "✅ Все задачи подтверждены!"
        try:
            await cb.message.edit_text(text, reply_markup=back_kb(lang, "admin"))
        except Exception:
            await cb.message.answer(text, reply_markup=back_kb(lang, "admin"))
        await cb.answer()
        return
    cnt  = len(tasks)
    rows = []
    for t in tasks:
        sent  = t.get("confirm_sent_count") or 0
        aname = (t.get("assignee_name") or "—")[:15]
        dl    = _fmt(t.get("deadline") or "")[:5]
        label = f"⏳ {t['title'][:20]} | {aname} | {dl} ({sent}x)"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"admin:resend_confirm:{t['id']}")])
    rows.append([InlineKeyboardButton(
        text="📨 Hammaga yuborish" if lang=="uz" else "📨 Отправить всем",
        callback_data="admin:resend_all_confirm"
    )])
    rows.append([InlineKeyboardButton(text=T(lang,"back"), callback_data="go:admin")])
    title = "Tasdiqlanmagan vazifalar" if lang=="uz" else "Неподтверждённые задачи"
    body  = str(cnt) + (" ta | Bosing — qayta yuboriladi" if lang=="uz" else " шт. | Нажмите — повторно")
    try:
        await cb.message.edit_text(
            f"<b>{title}</b>\n\n{body}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
            parse_mode="HTML"
        )
    except Exception:
        await cb.message.answer(
            f"<b>{title}</b>\n\n{body}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
            parse_mode="HTML"
        )
    await cb.answer()


@router.callback_query(F.data.startswith("admin:resend_confirm:"))
async def resend_confirm(cb: CallbackQuery):
    user = await db.get_user(cb.from_user.id)
    if not user or not is_admin(user):
        await cb.answer()
        return
    lang    = user["lang"]
    task_id = int(cb.data.split(":")[2])
    task    = await db.get_task(task_id)
    if not task:
        await cb.answer("Topilmadi", show_alert=True)
        return
    assignee = await db.get_user_by_id(task["assignee_id"])
    if not assignee:
        await cb.answer("Hodim topilmadi", show_alert=True)
        return
    a_lang = assignee.get("lang") or "uz"
    dl_fmt = _fmt(task.get("deadline") or "")
    notif  = (
        f"Vazifa tasdiqlanmagan!\n\n📋 {task['title']}\n📅 {dl_fmt}\n\nTasdiqlang:"
    ) if a_lang=="uz" else (
        f"Задача не подтверждена!\n\n📋 {task['title']}\n📅 {dl_fmt}\n\nПодтвердите:"
    )
    try:
        await cb.bot.send_message(
            assignee["telegram_id"], notif,
            reply_markup=_confirm_kb(task_id, a_lang)
        )
        await db.increment_confirm_sent(task_id)
        await cb.answer("Xabar yuborildi!" if lang=="uz" else "Отправлено!", show_alert=True)
    except Exception:
        await cb.answer("Yuborib bolmadi", show_alert=True)
        return
    cb.data = "admin:unconfirmed"
    await unconfirmed_tasks(cb)


@router.callback_query(F.data == "admin:resend_all_confirm")
async def resend_all_confirm(cb: CallbackQuery):
    user = await db.get_user(cb.from_user.id)
    if not user or not is_admin(user):
        await cb.answer()
        return
    lang  = user["lang"]
    tasks = await db.get_unconfirmed_tasks_admin()
    sent  = 0
    for task in tasks:
        assignee = await db.get_user_by_id(task["assignee_id"])
        if not assignee:
            continue
        a_lang = assignee.get("lang") or "uz"
        dl_fmt = _fmt(task.get("deadline") or "")
        notif  = (
            f"Vazifa tasdiqlanmagan!\n\n📋 {task['title']}\n📅 {dl_fmt}\n\nTasdiqlang:"
        ) if a_lang=="uz" else (
            f"Задача не подтверждена!\n\n📋 {task['title']}\n📅 {dl_fmt}\n\nПодтвердите:"
        )
        try:
            await cb.bot.send_message(
                task["telegram_id"], notif,
                reply_markup=_confirm_kb(task["id"], a_lang)
            )
            await db.increment_confirm_sent(task["id"])
            sent += 1
        except Exception:
            pass
    msg = str(sent) + (" ta yuborildi!" if lang=="uz" else " отправлено!")
    await cb.answer(msg, show_alert=True)
    cb.data = "admin:unconfirmed"
    await unconfirmed_tasks(cb)
