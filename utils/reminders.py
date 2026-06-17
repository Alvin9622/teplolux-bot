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


async def send_roadmap_reminders(bot: Bot):
    """Send alerts for overdue roadmap tasks (deadline passed, not done)."""
    from config import ADMIN_IDS
    overdue = await db.get_overdue_roadmap_tasks()
    if not overdue:
        return
    lines = ["🔴 <b>Kechikkan yo'l xarita vazifalari:</b>\n"]
    for t in overdue:
        dl = fmt_date(t.get("deadline") or "")
        assignee = f" | 👤 {t['assignee_name']}" if t.get("assignee_name") else ""
        lines.append(f"• <b>{t['title']}</b>\n  📅 {dl}{assignee}")
    text = "\n".join(lines)
    for aid in ADMIN_IDS:
        await safe_send(bot, aid, text)


async def send_weekly_report(bot: Bot):
    from config import ADMIN_IDS, GROUP_ID
    from utils.formatters import weekly_stats_text
    import database as _db
    today     = datetime.date.today()
    from_date = (today - datetime.timedelta(days=7)).isoformat()
    to_date   = today.isoformat()
    user_stats = await db.get_weekly_stats(from_date, to_date)
    text       = weekly_stats_text(user_stats, from_date, to_date, "uz")

    # Roadmap summary this week
    try:
        all_rm = await _db.get_roadmap_tasks()
        done_this_week = [
            t for t in all_rm
            if t.get("status") == "done" and t.get("updated_at", "") >= from_date
        ]
        if done_this_week:
            text += f"\n\n🗺 <b>Yo'l xarita — bu hafta bajarildi ({len(done_this_week)} ta):</b>\n"
            for t in done_this_week[:5]:
                text += f"  ✅ {t['title'][:40]}\n"
    except Exception:
        pass

    # Expense summary this week
    try:
        exps = await _db.get_expenses()
        week_exps = [e for e in exps if (e.get("created_at") or "") >= from_date]
        submitted = len(week_exps)
        approved  = sum(1 for e in week_exps if e.get("status") in ("approved", "paid"))
        if submitted:
            text += f"\n\n💰 <b>Xarajatlar bu hafta:</b>\n"
            text += f"  📋 Yuborildi: {submitted}\n"
            text += f"  ✅ Tasdiqlandi: {approved}\n"
    except Exception:
        pass

    for aid in ADMIN_IDS:
        await safe_send(bot, aid, text)
    if GROUP_ID:
        await safe_send(bot, GROUP_ID, text)


async def send_monthly_reports(bot: Bot, month: int, year: int):
    from config import ADMIN_IDS, GROUP_ID
    from utils.formatters import employee_monthly_report, monthly_stats_text
    from utils.excel_export import build_tasks_excel
    from aiogram.types import BufferedInputFile
    import database as _db
    users = await db.get_all_active_users()
    months_uz = ["Yanvar","Fevral","Mart","Aprel","May","Iyun",
                 "Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr"]
    for user in users:
        lang  = user.get("lang") or "uz"
        tasks = await db.get_employee_monthly_report(user["id"], month, year)
        text  = employee_monthly_report(user, tasks, month, year, lang)
        await safe_send(bot, user["telegram_id"], text)
    ss, us, plans = await db.get_monthly_stats(month, year)
    admin_text    = monthly_stats_text(ss, us, plans, month, year, "uz")

    # Expense report summary
    try:
        exp_stats = await _db.get_expense_stats(month, year)
        sc = exp_stats["status_counts"]
        ct = exp_stats["currency_totals"]
        admin_text += f"\n\n💰 <b>Xarajatlar hisoboti — {months_uz[month-1]} {year}:</b>\n"
        total_exp = sum(sc.values())
        admin_text += f"  Jami: {total_exp} ta\n"
        for currency in ("USD", "UZS", "RUB"):
            if ct.get(currency, 0) > 0:
                admin_text += f"  {currency}: {ct[currency]:,.0f}\n"
    except Exception:
        pass

    # Road map phase completion
    try:
        all_rm = await _db.get_roadmap_tasks()
        admin_text += "\n🗺 <b>Yo'l xarita holati:</b>\n"
        for phase in ("1-3", "4-6", "7-9", "10-18"):
            pts = [t for t in all_rm if t["phase"] == phase]
            d = sum(1 for t in pts if t["status"] == "done")
            total = len(pts)
            pct = round(d/total*100) if total else 0
            admin_text += f"  Bosqich {phase}: {d}/{total} ({pct}%)\n"
    except Exception:
        pass

    all_tasks = await db.get_all_tasks_for_export(month, year)
    fname = f"teplolux_{months_uz[month-1].lower()}_{year}.xlsx"
    targets = list(ADMIN_IDS)
    if GROUP_ID:
        targets.append(GROUP_ID)
    for target in targets:
        await safe_send(bot, target, admin_text)
        if all_tasks:
            try:
                buf = build_tasks_excel(all_tasks, month, year)
                doc = BufferedInputFile(buf.read(), filename=fname)
                await bot.send_document(
                    target, doc,
                    caption=f"📊 Excel hisobot — {months_uz[month-1]} {year} | {len(all_tasks)} ta vazifa",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error("Monthly Excel send error %s: %s", target, e)


async def send_pending_expense_reminders(bot: Bot):
    """3 kundan ortiq 'pending' turgan xarajatlar haqida adminlarga eslatma."""
    try:
        expenses = await db.get_expenses(status="pending")
        now = datetime.datetime.now()
        old_expenses = []
        for exp in expenses:
            try:
                created = datetime.datetime.fromisoformat(exp["created_at"])
                days_old = (now - created).days
                if days_old >= 3:
                    old_expenses.append((exp, days_old))
            except Exception:
                pass
        if not old_expenses:
            return
        lines = ["⏳ <b>Tasdiqlanmagan xarajatlar:</b>\n"]
        for exp, days in old_expenses:
            lines.append(f"• {exp['name']} — {exp['amount']} {exp['currency']} ({days} kun kutmoqda)")
        text = "\n".join(lines)
        for admin_id in ADMIN_IDS:
            await safe_send(bot, admin_id, text)
    except Exception as e:
        logger.error("send_pending_expense_reminders error: %s", e)
