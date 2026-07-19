import asyncio
import datetime
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeChat
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN, ADMIN_IDS
from database import init_db, seed_roadmap_tasks, get_all_employee_ids, get_plan_items
from handlers import admin, employee, common, confirm, group, roadmap, expenses
from handlers import budget, activity, dashboard, inline as inline_handler, ideas
from handlers import workplan, kpi, content as content_handler, qr, time_management
from utils.pomodoro import rehydrate_pomodoros
from utils.time_blocks import rehydrate_time_blocks
from utils.time_stats import build_week_report
from keyboards.time_kb import time_menu_kb
from database import get_last_activity
from utils.reminders import (
    send_reminders, send_daily_digest,
    send_confirm_reminders, send_weekly_report,
    send_monthly_reports, send_roadmap_reminders,
    send_pending_expense_reminders
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    user_cmds = [
        BotCommand(command="start",   description="🏠 Asosiy menyu"),
        BotCommand(command="mytasks", description="📋 Mening vazifalarim"),
        BotCommand(command="help",    description="📖 Yo'riqnoma"),
        BotCommand(command="bekor",   description="❌ Jarayonni bekor qilish"),
    ]
    admin_cmds = [
        BotCommand(command="start",   description="🏠 Asosiy menyu"),
        BotCommand(command="admin",   description="⚙️ Admin paneli"),
        BotCommand(command="mytasks", description="📋 Vazifalar"),
        BotCommand(command="help",    description="📖 Yo'riqnoma"),
        BotCommand(command="bekor",   description="❌ Bekor qilish"),
    ]
    for aid in ADMIN_IDS:
        try:
            await bot.set_my_commands(admin_cmds, scope=BotCommandScopeChat(chat_id=aid))
        except Exception:
            pass
    await bot.set_my_commands(user_cmds)


async def main():
    await init_db()
    await seed_roadmap_tasks()

    # Google Sheets — startup sync (xato bo'lsa bot ishini davom ettiradi)
    try:
        from utils.sheets import full_sync_all_tasks
        await full_sync_all_tasks()
    except Exception as _se:
        logger.warning("Sheets startup sync skipped: %s", _se)

    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher(storage=MemoryStorage())

    dp.include_router(common.router)
    dp.include_router(admin.router)
    dp.include_router(employee.router)
    dp.include_router(confirm.router)
    dp.include_router(group.router)
    dp.include_router(roadmap.router)
    dp.include_router(expenses.router)
    dp.include_router(budget.router)
    dp.include_router(activity.router)
    dp.include_router(dashboard.router)
    dp.include_router(inline_handler.router)
    dp.include_router(ideas.router)
    dp.include_router(workplan.router)
    dp.include_router(kpi.router)
    dp.include_router(content_handler.router)
    dp.include_router(qr.router)
    dp.include_router(time_management.router)

    await set_commands(bot)

    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
    # Kunlik digest 09:00
    scheduler.add_job(send_daily_digest,      "cron", hour=9,       minute=0,  args=[bot])
    # Eslatmalar 09:30 va 15:30
    scheduler.add_job(send_reminders,         "cron", hour="9,15",  minute=30, args=[bot])
    # Tasdiqlanmagan vazifalar — har soatda
    scheduler.add_job(send_confirm_reminders, "cron", minute=0,                args=[bot])
    # Haftalik hisobot — dushanba 09:00
    scheduler.add_job(send_weekly_report,     "cron", day_of_week="mon", hour=9, minute=0, args=[bot])
    # Yo'l xarita kechikkan vazifalar — har kuni 09:00
    scheduler.add_job(send_roadmap_reminders,          "cron", hour=9,  minute=0,  args=[bot])
    # Kutilayotgan xarajatlar eslatmasi — har kuni 10:00
    scheduler.add_job(send_pending_expense_reminders,  "cron", hour=10, minute=0,  args=[bot])
    # Oylik hisobot — har oyning 1-kuni 10:00
    async def _monthly_report():
        now = datetime.datetime.now()
        m   = now.month - 1 or 12
        y   = now.year if now.month > 1 else now.year - 1
        await send_monthly_reports(bot, m, y)
    scheduler.add_job(_monthly_report, "cron", day=1, hour=10, minute=0)

    # ── Vaqt boshqaruvi eslatmalari ──
    async def morning_plan_prompt():
        for uid in await get_all_employee_ids():
            try:
                await bot.send_message(
                    uid,
                    "☀️ <b>Xayrli tong!</b>\n\n"
                    "Bugungi kuningizni rejalashtiring. "
                    "Eng muhim 3 ta ishingiz qaysi?\n\n"
                    "«📋 Kunlik reja» → «➕ Yangi reja tuzish»",
                    reply_markup=time_menu_kb(), parse_mode="HTML")
            except Exception:
                pass

    async def evening_plan_review():
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        for uid in await get_all_employee_ids():
            items = await get_plan_items(uid, today)
            if not items:
                continue
            done = sum(1 for i in items if i["is_done"])
            tail = ("🎉 Ajoyib kun! Hammasini uddaladingiz."
                    if done == len(items)
                    else "Bajarilmaganlarini ertaga rejaga qo'shing.")
            try:
                await bot.send_message(
                    uid,
                    f"🌙 <b>Kun yakuni</b>\n\n"
                    f"Bugungi reja: {done}/{len(items)} bajarildi.\n{tail}",
                    parse_mode="HTML")
            except Exception:
                pass

    async def weekly_focus_report():
        from aiogram.types import BufferedInputFile
        from utils.time_stats import build_week_chart
        for uid in await get_all_employee_ids():
            try:
                text  = await build_week_report(uid)
                chart = await build_week_chart(uid)
                if chart:
                    await bot.send_photo(
                        uid, BufferedInputFile(chart, "week.png"),
                        caption="📅 <b>Haftalik yakun</b>\n\n" + text,
                        parse_mode="HTML")
                else:
                    await bot.send_message(uid, "📅 <b>Haftalik yakun</b>\n\n" + text,
                                           parse_mode="HTML")
            except Exception:
                pass

    # ── Aqlli eslatma (nudge) — ish vaqtida uzoq faollik bo'lmasa ──
    async def inactivity_nudge():
        now = datetime.datetime.now()
        if now.weekday() >= 5:      # shanba/yakshanba
            return
        for uid in await get_all_employee_ids():
            last = await get_last_activity(uid)
            if not last:
                continue
            if last.strftime("%Y-%m-%d") != now.strftime("%Y-%m-%d"):
                continue
            if (now - last) >= datetime.timedelta(hours=2):
                try:
                    await bot.send_message(
                        uid,
                        "🔔 <b>2 soatdan beri faollik yo'q</b>\n\n"
                        "Nima ustida ishlayapsiz? Vaqtni ▶️ belgilab qo'ying "
                        "yoki 🍅 pomodoro bilan fokusga qayting.",
                        parse_mode="HTML")
                except Exception:
                    pass

    scheduler.add_job(morning_plan_prompt,  "cron", hour=9,  minute=0)
    scheduler.add_job(evening_plan_review,  "cron", hour=18, minute=0)
    scheduler.add_job(weekly_focus_report,  "cron", day_of_week="fri", hour=18, minute=0)
    for hh, mm in [(11, 30), (14, 30), (16, 30)]:
        scheduler.add_job(inactivity_nudge, "cron", hour=hh, minute=mm)
    scheduler.start()

    # Faol taymerlarni tiklash (restartdan keyin)
    try:
        await rehydrate_pomodoros(scheduler, bot)
        await rehydrate_time_blocks(scheduler, bot)
    except Exception as _pe:
        logger.warning("Timer rehydrate skipped: %s", _pe)

    # Mini App web server
    webapp_runner = None
    try:
        from webapp_server import start_webapp
        webapp_runner = await start_webapp()
        logger.info("Mini App web server started ✅")
    except Exception as _we:
        logger.warning("Mini App server skipped: %s", _we)

    logger.info("Bot ishga tushdi ✅")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(),
                               scheduler=scheduler)
    finally:
        scheduler.shutdown()
        if webapp_runner:
            await webapp_runner.cleanup()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
