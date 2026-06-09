import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeChat
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN, ADMIN_IDS
from database import init_db
from handlers import admin, employee, common, confirm
from utils.reminders import (
    send_reminders, send_daily_digest,
    send_confirm_reminders, send_weekly_report
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
        BotCommand(command="bekor",   description="❌ Jarayonni bekor qilish"),
    ]
    admin_cmds = [
        BotCommand(command="start",   description="🏠 Asosiy menyu"),
        BotCommand(command="admin",   description="⚙️ Admin paneli"),
        BotCommand(command="mytasks", description="📋 Vazifalar"),
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

    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher(storage=MemoryStorage())

    dp.include_router(common.router)
    dp.include_router(admin.router)
    dp.include_router(employee.router)
    dp.include_router(confirm.router)

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
    scheduler.start()

    logger.info("Bot ishga tushdi ✅")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
