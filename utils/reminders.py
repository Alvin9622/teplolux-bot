import datetime
import logging
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

import database as db
from texts import T, status_txt

logger = logging.getLogger(__name__)


def fmt_date(iso):
    try:
        return datetime.date.fromisoformat(iso[:10]).strftime("%d.%m.%Y")
    except Exception:
        return iso or "—"


async def safe_send(bot: Bot, chat_id: int, text: str, **kwargs):
    try:
        await bot.send_message(chat_id, text, parse_mode="HTML", **kwargs)
        return True
    except TelegramForbiddenError:
        logger.warning("Blocked by %s", chat_id)
    except TelegramBadRequest as e:
        logger.error("BadRequest %s: %s", chat_id, e)
    except Exception as e:
        logger.error("Error %s: %s", chat_id, e)
    return False


async def send_reminders(bot: Bot):
    for days, rtype in [(3, "3days"), (1, "1day")]:
        tasks = await db.get_tasks_near_deadline(days)
        for task in tasks:
            if await db.check_reminder_sent(task["id"], rtype):
                continue
            lang = task.get("lang") or "uz"
            key  = "notif_3days" if days == 3 else "notif_1day"
            text = T(lang, key,
                     title=task["title"],
                     status=status_txt(lang, task["status"]),
                     pct=task.get("progress_pct") or 0,
                     deadline=fmt_date(task.get("deadline")))
            await safe_send(bot, task["telegram_id"], text)
            await db.mark_reminder_sent(task["id"], rtype)

    for task in await db.get_overdue_tasks():
        if await db.check_reminder_sent(task["id"], "overdue"):
            continue
        lang = task.get("lang") or "uz"
        text = T(lang, "notif_overdue",
                 title=task["title"],
                 status=status_txt(lang, task["status"]),
                 pct=task.get("progress_pct") or 0,
                 deadline=fmt_date(task.get("deadline")))
        await safe_send(bot, task["telegram_id"], text)
        await db.mark_reminder_sent(task["id"], "overdue")

    for task in await db.get_tasks_with_custom_reminder():
        r_days = task.get("reminder_days") or 0
        if r_days == 0:
            continue
        created = datetime.date.fromisoformat(task["created_at"][:10])
        delta   = (datetime.date.today() - created).days
        if delta % r_days != 0:
            continue
        rtype = f"custom_{datetime.date.today().isoformat()}"
        if await db.check_reminder_sent(task["id"], rtype):
            continue
        lang = task.get("lang") or "uz"
        text = T(lang, "notif_reminder",
                 title=task["title"],
                 status=status_txt(lang, task["status"]),
                 pct=task.get("progress_pct") or 0,
                 deadline=fmt_date(task.get("deadline")))
        await safe_send(bot, task["telegram_id"], text)
        await db.mark_reminder_sent(task["id"], rtype)


async def send_confirm_reminders(bot: Bot):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    tasks = await db.get_unconfirmed_tasks()
    for task in tasks:
        sent = task.get("confirm_sent_count") or 0
        if sent >= 3:
            continue
        lang   = task.get("lang") or "uz"
        dl_fmt = fmt_date(task.get("deadline") or "")
        if lang == "uz":
            notif = f"Vazifa tasdiqlanmagan!\n\n📋 {task['title']}\n📅 {dl_fmt}\n\nTasdiqlang:"
        else:
            notif = f"Задача не подтверждена!\n\n📋 {task['title']}\n📅 {dl_fmt}\n\nПодтвердите:"
        confirm_kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="✅ Qabul qildim" if lang=="uz" else "✅ Принял",
                callback_data=f"task:confirm:{task['id']}"
            )
        ]])
        await safe_send(bot, task["telegram_id"], notif, reply_markup=confirm_kb)
        await db.increment_confirm_sent(task["id"])


async def send_daily_digest(bot: Bot):
    users = await db.get_all_active_users()
    for user in users:
        tasks = await db.get_user_tasks_for_digest(user["id"])
        lang  = user.get("lang") or "uz"
        name  = user["full_name"].split()[0]
        if not tasks:
            await safe_send(bot, user["telegram_id"], T(lang, "digest_empty", name=name))
            continue
        text = T(lang, "digest_header", name=name)
        for i, task in enumerate(tasks[:10], 1):
            icon  = {"new":"🆕","in_progress":"🔄","done":"✅","cancelled":"❌","review":"👀"}.get(task["status"],"📌")
            from utils.formatters import days_left_str
            extra = days_left_str(task.get("deadline"), lang)
            text += T(lang, "digest_item",
                      i=i, title=task["title"],
                      status=icon+" "+status_txt(lang, task["status"]),
                      pct=task.get("progress_pct") or 0,
                      deadline=fmt_date(task.get("deadline")), extra=extra)
        if len(tasks) > 10:
            text += f"... +{len(tasks)-10} ta" if lang=="uz" else f"... +{len(tasks)-10} задач"
        await safe_send(bot, user["telegram_id"], text)


async def send_weekly_report(bot: Bot):
    from config import ADMIN_IDS, GROUP_ID
    from utils.formatters import weekly_stats_text
    today     = datetime.date.today()
    from_date = (today - datetime.timedelta(days=7)).isoformat()
    to_date   = today.isoformat()
    user_stats = await db.get_weekly_stats(from_date, to_date)
    text       = weekly_stats_text(user_stats, from_date, to_date, "uz")
    for aid in ADMIN_IDS:
        await safe_send(bot, aid, text)
    if GROUP_ID:
        await safe_send(bot, GROUP_ID, text)


async def send_monthly_reports(bot: Bot, month: int, year: int):
    from config import ADMIN_IDS, GROUP_ID
    from utils.formatters import employee_monthly_report, monthly_stats_text
    users = await db.get_all_active_users()
    for user in users:
        lang  = user.get("lang") or "uz"
        tasks = await db.get_employee_monthly_report(user["id"], month, year)
        text  = employee_monthly_report(user, tasks, month, year, lang)
        await safe_send(bot, user["telegram_id"], text)
    ss, us, plans = await db.get_monthly_stats(month, year)
    admin_text    = monthly_stats_text(ss, us, plans, month, year, "uz")
    for aid in ADMIN_IDS:
        await safe_send(bot, aid, admin_text)
    if GROUP_ID:
        await safe_send(bot, GROUP_ID, admin_text)
