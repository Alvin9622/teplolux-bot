import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery

import database as db
from config import ADMIN_IDS
from keyboards.kb import activity_log_kb
from texts import T

router = Router()


def is_admin(user):
    return user and (user["role"] == "admin" or user["telegram_id"] in ADMIN_IDS)


async def _get_ul(tg_id):
    user = await db.get_user(tg_id)
    return user, (user["lang"] if user else "uz")


def _fmt_log_entry(entry):
    try:
        dt = datetime.datetime.strptime(entry["created_at"][:16], "%Y-%m-%d %H:%M")
        dt_str = dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        dt_str = (entry.get("created_at") or "")[:16]

    entity = f"{entry['entity_type']} #{entry['entity_id']}"
    action = entry.get("action") or ""
    old = entry.get("old_value") or ""
    new = entry.get("new_value") or ""
    actor = entry.get("actor_name") or "?"
    username = entry.get("actor_username")
    actor_str = f"@{username}" if username else actor

    change = f"{action}"
    if old and new:
        change = f"{action}: {old} → {new}"
    elif new:
        change = f"{action}: {new}"

    return f"🕐 {dt_str} | {entity} | {change} | {actor_str}"


@router.callback_query(F.data.startswith("activity:log:"))
async def activity_log_view(cb: CallbackQuery):
    user, lang = await _get_ul(cb.from_user.id)
    if not is_admin(user):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    offset = int(cb.data.split(":")[2])
    limit = 20
    entries = await db.get_activity_log(limit=limit + 1, offset=offset)
    has_more = len(entries) > limit
    entries = entries[:limit]

    title = T(lang, "activity_log_title")
    if not entries:
        text = f"{title}\n\n{T(lang, 'activity_empty')}"
    else:
        lines = [title, ""]
        for entry in entries:
            lines.append(_fmt_log_entry(entry))
        text = "\n".join(lines)

    kb = activity_log_kb(lang, offset, has_more)
    try:
        await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await cb.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await cb.answer()
