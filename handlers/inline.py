from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
import hashlib

import database as db

router = Router()


def _task_status_icon(status):
    return {"new": "🆕", "in_progress": "🔄", "done": "✅",
            "cancelled": "❌", "review": "👀"}.get(status, "📌")


def _exp_status_icon(status):
    return {"pending": "⏳", "approved": "✅", "rejected": "❌",
            "postponed": "🔄", "paid": "💳"}.get(status, "❓")


def _uid(prefix, item_id):
    raw = f"{prefix}:{item_id}"
    return hashlib.md5(raw.encode()).hexdigest()


@router.inline_query()
async def inline_search(query: InlineQuery):
    q = (query.query or "").strip().lower()
    results = []

    # Search roadmap tasks
    try:
        tasks = await db.get_roadmap_tasks()
        for task in tasks:
            title = task.get("title") or ""
            if not q or q in title.lower() or q in (task.get("notes") or "").lower():
                icon = "✅" if task["status"] == "done" else "⬜"
                assignee = task.get("assignee_name") or ""
                deadline = task.get("deadline") or ""
                desc_parts = [f"Holat: {icon} {task['status']}"]
                if assignee:
                    desc_parts.append(f"👤 {assignee}")
                if deadline:
                    desc_parts.append(f"📅 {deadline}")
                desc = " | ".join(desc_parts)
                text = (
                    f"🗺 <b>{title}</b>\n"
                    f"Bosqich: {task.get('phase')}\n"
                    f"{desc}"
                )
                results.append(InlineQueryResultArticle(
                    id=_uid("rm", task["id"]),
                    title=f"🗺 {title[:50]}",
                    description=desc[:100],
                    input_message_content=InputTextMessageContent(
                        message_text=text, parse_mode="HTML"
                    ),
                ))
                if len(results) >= 25:
                    break
    except Exception:
        pass

    # Search expenses (fill remaining slots)
    if len(results) < 25:
        try:
            expenses = await db.get_expenses()
            for exp in expenses:
                name = exp.get("name") or ""
                if not q or q in name.lower() or q in (exp.get("note") or "").lower():
                    icon = _exp_status_icon(exp.get("status"))
                    date = (exp.get("created_at") or "")[:10]
                    desc = f"{exp.get('amount')} {exp.get('currency')} | {icon} {exp.get('status')} | {date}"
                    text = (
                        f"💰 <b>{name}</b>\n"
                        f"💵 {exp.get('amount')} {exp.get('currency')}\n"
                        f"Holat: {icon} {exp.get('status')}\n"
                        f"📅 {date}"
                    )
                    results.append(InlineQueryResultArticle(
                        id=_uid("exp", exp["id"]),
                        title=f"💰 {name[:50]}",
                        description=desc[:100],
                        input_message_content=InputTextMessageContent(
                            message_text=text, parse_mode="HTML"
                        ),
                    ))
                    if len(results) >= 25:
                        break
        except Exception:
            pass

    await query.answer(results[:50], cache_time=10, is_personal=True)
