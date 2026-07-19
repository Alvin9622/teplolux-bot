"""Vaqt bloklari eslatma mantig'i — restart-proof (pomodoro bilan bir xil)."""
import datetime
import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import database as db
from keyboards.time_kb import block_action_kb, PRIORITY_EMOJI

logger = logging.getLogger(__name__)


def block_start_dt(block_date: str, start_time: str) -> datetime.datetime:
    return datetime.datetime.strptime(f"{block_date} {start_time}", "%Y-%m-%d %H:%M")


async def send_block_reminder(bot: Bot, user_id: int, block_id: int):
    """Blok boshlanish vaqtida chaqiriladi (APScheduler job)."""
    block = await db.get_time_block(block_id)
    if not block or block["status"] != "planned" or block["reminded"]:
        return
    await db.mark_block_reminded(block_id)
    prio = PRIORITY_EMOJI.get(block["priority"], "")
    text = (
        "⏳ <b>Vaqt bloki boshlandi</b>\n\n"
        f"{prio} <b>{block['title']}</b>\n"
        f"🕒 {block['start_time']}–{block['end_time']}  ·  {block['category']}\n\n"
        "📵 Boshqa ishlarni chetga qo'ying — faqat shunga fokuslaning. 🎯"
    )
    try:
        await bot.send_message(user_id, text,
                               reply_markup=block_action_kb(block_id),
                               parse_mode="HTML")
    except Exception as e:
        logger.warning("send_block_reminder error: %s", e)


def schedule_block_reminder(scheduler: AsyncIOScheduler, bot: Bot,
                            user_id: int, block_id: int, run_dt: datetime.datetime):
    scheduler.add_job(
        send_block_reminder, trigger="date", run_date=run_dt,
        args=[bot, user_id, block_id],
        id=f"block_{block_id}", replace_existing=True)


async def rehydrate_time_blocks(scheduler: AsyncIOScheduler, bot: Bot):
    """Bot restartda bugungi kelajakdagi bloklarni qayta rejalashtiradi."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    now = datetime.datetime.now()
    count = 0
    for b in await db.get_blocks_for_reminder(today):
        run_dt = block_start_dt(b["block_date"], b["start_time"])
        if run_dt > now:
            schedule_block_reminder(scheduler, bot, b["user_id"], b["id"], run_dt)
            count += 1
    logger.info("Rehydrated %d time block reminder(s)", count)
