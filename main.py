import asyncio
import datetime
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeChat
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN, ADMIN_IDS
from database import init_db, seed_roadmap_tasks
from handlers import admin, employee, common, confirm, group, roadmap, expenses
from utils.reminders import (
    send_reminders, send_daily_digest,
    send_confirm_reminders, send_weekly_report,
    send_monthly_reports
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
    # Oylik hisobot — har oyning 1-kuni 10:00
    async def _monthly_report():
        now = datetime.datetime.now()
        m   = now.month - 1 or 12
        y   = now.year if now.month > 1 else now.year - 1
        await send_monthly_reports(bot, m, y)
    scheduler.add_job(_monthly_report, "cron", day=1, hour=10, minute=0)
    scheduler.start()

    logger.info("Bot ishga tushdi ✅")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
