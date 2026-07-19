"""Pomodoro taymer mantig'i — restartda tiklanadigan sessiyalar."""
import datetime
import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import database as db
from keyboards.time_kb import pomodoro_done_kb

logger = logging.getLogger(__name__)


async def send_pomodoro_complete(bot: Bot, user_id: int, session_id: int):
    """Pomodoro tugaganda chaqiriladi (APScheduler job)."""
    session = await db.get_pomodoro_session(session_id)
    if not session or session["status"] != "active":
        return  # allaqachon bekor qilingan yoki tugagan

    await db.complete_pomodoro(session_id)
    stats = await db.get_focus_stats(user_id)
    today_count = await db.count_today_pomodoros(user_id)

    text = (
        "🍅 <b>Pomodoro tugadi!</b>\n\n"
        f"✅ {session['planned_minutes']} daqiqa fokus bajarildi\n"
        f"⭐ +10 fokus ball (jami: {stats['focus_points']})\n"
        f"🔢 Bugungi pomodorolar: {today_count}\n\n"
        "☕️ 5 daqiqa dam oling — cho'zing, suv iching, ekrandan uzoqlashing."
    )
    try:
        await bot.send_message(user_id, text, reply_markup=pomodoro_done_kb(),
                               parse_mode="HTML")
    except Exception as e:
        logger.warning("send_pomodoro_complete error: %s", e)


def schedule_pomodoro(scheduler: AsyncIOScheduler, bot: Bot,
                      user_id: int, session_id: int, ends_at: datetime.datetime):
    """Pomodoro tugash vaqtiga bir martalik job qo'yadi."""
    scheduler.add_job(
        send_pomodoro_complete,
        trigger="date",
        run_date=ends_at,
        args=[bot, user_id, session_id],
        id=f"pomodoro_{session_id}",
        replace_existing=True,
    )


async def rehydrate_pomodoros(scheduler: AsyncIOScheduler, bot: Bot):
    """Bot qayta ishga tushganda faol pomodorolarni tiklaydi."""
    active = await db.get_active_pomodoros()
    now = datetime.datetime.now()
    for s in active:
        ends_at = datetime.datetime.fromisoformat(s["ends_at"])
        if ends_at <= now:
            # bot o'chiq paytida tugagan — darhol xabar ber
            await send_pomodoro_complete(bot, s["user_id"], s["id"])
        else:
            schedule_pomodoro(scheduler, bot, s["user_id"], s["id"], ends_at)
    logger.info("Rehydrated %d active pomodoro(s)", len(active))
