"""AI yordamchi — tabiiy tildan vaqt yozish va kunlik tavsiya (Claude Haiku)."""
import datetime
import json
import logging

from config import ANTHROPIC_API_KEY
import database as db
from keyboards.time_kb import CATEGORIES

logger = logging.getLogger(__name__)

MODEL = "claude-haiku-4-5-20251001"   # arzon va tez

_client = None


def _get_client():
    """anthropic klientini lazy yaratadi (kutubxona/kalit yo'q bo'lsa None)."""
    global _client
    if not ANTHROPIC_API_KEY:
        return None
    if _client is None:
        try:
            from anthropic import AsyncAnthropic
            _client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        except Exception as e:
            logger.warning("Anthropic client init error: %s", e)
            return None
    return _client


def is_ai_available() -> bool:
    return _get_client() is not None


def _clean_json(text: str) -> str:
    return text.strip().replace("```json", "").replace("```", "").strip()


async def parse_time_entry(text: str):
    """Tabiiy tildan {category, minutes, task} ajratadi (yoki None)."""
    client = _get_client()
    if not client:
        return None
    prompt = (
        "Foydalanuvchi vaqt sarfini tabiiy tilda yozdi. Undan ma'lumot ajrat.\n"
        f"Mavjud kategoriyalar: {', '.join(CATEGORIES)}\n"
        f'Matn: "{text}"\n\n'
        "Faqat JSON qaytar, boshqa hech narsa:\n"
        '{"category": "<kategoriyalardan biri yoki Boshqa>", '
        '"minutes": <butun son>, "task": "<qisqa ish nomi>"}'
    )
    try:
        msg = await client.messages.create(
            model=MODEL, max_tokens=200,
            messages=[{"role": "user", "content": prompt}])
        data = json.loads(_clean_json(msg.content[0].text))
        if not isinstance(data.get("minutes"), int) or data["minutes"] <= 0:
            return None
        data["task"] = str(data.get("task", "Ish"))[:60]
        return data
    except Exception as e:
        logger.warning("parse_time_entry error: %s", e)
        return None


async def daily_suggestion(user_id: int) -> str:
    """O'tmish + maqsadlar asosida bugungi 3 ishni taklif qiladi."""
    client = _get_client()
    if not client:
        return "🤖 AI sozlanmagan (ANTHROPIC_API_KEY yo'q)."
    since = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    by_cat = await db.time_by_category_since(user_id, since)
    ctx_cat = ", ".join(f"{c}: {round(s/3600,1)}s" for c, s in by_cat) or "ma'lumot yo'q"
    goals = await db.get_goals(user_id)
    goal_parts = []
    for g in goals:
        cur = await db.compute_goal_current(g)
        goal_parts.append(f"{g['title']} ({cur}/{g['target_value']} {g['unit']})")
    ctx_goals = "; ".join(goal_parts) or "maqsad yo'q"
    prompt = (
        "Sen marketing xodimining shaxsiy samaradorlik yordamchisisan. "
        "Faqat o'zbek tilida, qisqa javob ber.\n"
        f"So'nggi 7 kun vaqt taqsimoti: {ctx_cat}\n"
        f"Faol maqsadlar: {ctx_goals}\n\n"
        "Bugun uchun eng muhim 3 ta ishni taklif qil. Har biri bitta qisqa "
        "qator, maqsadlarga bog'langan. Kirish gapsiz, faqat ro'yxat."
    )
    try:
        msg = await client.messages.create(
            model=MODEL, max_tokens=350,
            messages=[{"role": "user", "content": prompt}])
        return msg.content[0].text.strip()
    except Exception as e:
        logger.warning("daily_suggestion error: %s", e)
        return "🤖 Tavsiya olishда xatolik. Keyinroq urinib ko'ring."
