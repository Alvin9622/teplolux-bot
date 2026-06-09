"""
Guruh handleri.

Admin guruhda quyidagi formatda yozsa, bot vazifa yaratadi:

  /vazifa @username Vazifa matni | 25.06.2025
  /vazifa @username Vazifa matni          (muddatsiz — 7 kun default)

Yoki oddiy mention bilan (admin tasdiqlab yuboradi):
  @username shu ishni qiling | 30.06.2025
"""

import datetime
import re
import hashlib
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

import database as db
from config import ADMIN_IDS
from texts import T, priority_txt, reminder_txt

router = Router()


def _is_admin(telegram_id: int) -> bool:
    return telegram_id in ADMIN_IDS


def _parse_deadline(text: str):
    m = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', text)
    if m:
        try:
            return datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            pass
    return None


def _clean_title(text: str) -> str:
    text = re.sub(r'^/vazifa\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'\d{1,2}\.\d{1,2}\.\d{4}', '', text)
    text = re.sub(r'\|', '', text)
    return ' '.join(text.split()).strip()


async def _find_user_by_username(username: str):
    username = username.lstrip('@').lower()
    for u in await db.get_all_active_users():
        if u.get('username') and u['username'].lower() == username:
            return u
    return None


def _short_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:8]


async def _create_and_notify(bot, title, assignee, creator_id, dl_str):
    """Vazifa yaratib, hodimga xabar yuboradi. task_id qaytaradi."""
    task_id = await db.create_task(
        title=title,
        description="Guruhdan yaratildi",
        category="📦 Boshqa",
        assignee_id=assignee["id"],
        created_by=creator_id,
        deadline=dl_str,
        priority="medium",
        reminder_days=0
    )
    a_lang = assignee.get("lang") or "uz"
    dl_fmt = datetime.date.fromisoformat(dl_str).strftime("%d.%m.%Y")
    notif  = T(a_lang, "notif_new_task",
               title=title, category="📦 Boshqa",
               description="Guruhdan tayinlandi",
               deadline=dl_fmt,
               priority=priority_txt(a_lang, "medium"),
               reminder=reminder_txt(a_lang, 0))
    confirm_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="✅ Qabul qildim" if a_lang == "uz" else "✅ Принял",
            callback_data=f"task:confirm:{task_id}"
        )
    ]])
    sent = False
    try:
        await bot.send_message(assignee["telegram_id"], notif,
                               reply_markup=confirm_kb, parse_mode="HTML")
        sent = True
    except Exception:
        pass
    return task_id, dl_fmt, sent


# ═══════════════════════════════════════════════════════════════
# /vazifa komandasi
# ═══════════════════════════════════════════════════════════════

@router.message(Command("vazifa"), F.chat.type.in_({"group", "supergroup"}))
async def cmd_group_vazifa(msg: Message):
    if not _is_admin(msg.from_user.id):
        return

    text     = msg.text or ""
    mentions = re.findall(r'@(\w+)', text)

    if not mentions:
        await msg.reply(
            "❌ <b>Format noto'g'ri.</b>\n\n"
            "To'g'ri:\n"
            "<code>/vazifa @username Vazifa matni | 25.06.2025</code>\n\n"
            "Muddat ixtiyoriy (ko'rsatilmasa 7 kun).",
            parse_mode="HTML"
        )
        return

    assignee = await _find_user_by_username(mentions[0])
    if not assignee:
        await msg.reply(
            f"❌ <b>@{mentions[0]}</b> topilmadi.\n"
            "Hodim botda ro'yxatdan o'tgan bo'lishi kerak.",
            parse_mode="HTML"
        )
        return

    title = _clean_title(text)
    if not title:
        await msg.reply("❌ Vazifa matnini kiriting.", parse_mode="HTML")
        return

    deadline = _parse_deadline(text)
    dl_str   = deadline.isoformat() if deadline else (
        datetime.date.today() + datetime.timedelta(days=7)
    ).isoformat()

    creator    = await db.get_user(msg.from_user.id)
    creator_id = creator["id"] if creator else None

    task_id, dl_fmt, sent = await _create_and_notify(
        msg.bot, title, assignee, creator_id, dl_str
    )

    status = "✅ Xabar yuborildi" if sent else "⚠️ Xabar yuborib bo'lmadi"
    await msg.reply(
        f"📌 <b>Vazifa yaratildi!</b>\n\n"
        f"📋 {title}\n"
        f"👤 {assignee['full_name']} (@{mentions[0]})\n"
        f"📅 {dl_fmt}\n"
        f"🆔 #{task_id}\n\n{status}",
        parse_mode="HTML"
    )


# ═══════════════════════════════════════════════════════════════
# @mention bilan oddiy xabar — admin tasdiqlaydi
# ═══════════════════════════════════════════════════════════════

@router.message(F.chat.type.in_({"group", "supergroup"}), F.text.regexp(r'^@\w+\s+\S+'))
async def group_mention_task(msg: Message):
    if not _is_admin(msg.from_user.id):
        return

    text     = msg.text or ""
    mentions = re.findall(r'@(\w+)', text)
    if not mentions:
        return

    assignee = await _find_user_by_username(mentions[0])
    if not assignee:
        return  # Jimgina o'tkazib yuboramiz

    title = _clean_title(text)
    if not title or len(title) < 3:
        return

    deadline = _parse_deadline(text)
    dl_str   = deadline.isoformat() if deadline else (
        datetime.date.today() + datetime.timedelta(days=7)
    ).isoformat()
    dl_fmt   = datetime.date.fromisoformat(dl_str).strftime("%d.%m.%Y")
    h        = _short_hash(title)

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="✅ Ha, vazifa yarat",
            callback_data=f"grp:ok:{assignee['id']}:{dl_str}:{h}"
        ),
        InlineKeyboardButton(text="❌ Yo'q", callback_data="grp:no")
    ]])
    await msg.reply(
        f"📌 <b>Vazifa yaratayinmi?</b>\n\n"
        f"📋 {title}\n"
        f"👤 {assignee['full_name']} (@{mentions[0]})\n"
        f"📅 {dl_fmt}",
        reply_markup=kb, parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("grp:ok:"))
async def grp_confirm(cb: CallbackQuery):
    if not _is_admin(cb.from_user.id):
        await cb.answer()
        return

    parts       = cb.data.split(":")
    assignee_id = int(parts[2])
    dl_str      = parts[3]
    assignee    = await db.get_user_by_id(assignee_id)
    if not assignee:
        await cb.answer("Hodim topilmadi", show_alert=True)
        return

    orig  = cb.message.reply_to_message
    title = _clean_title(orig.text or "") if orig else "Guruhdan vazifa"
    if not title:
        title = "Guruhdan vazifa"

    creator    = await db.get_user(cb.from_user.id)
    creator_id = creator["id"] if creator else None

    task_id, dl_fmt, sent = await _create_and_notify(
        cb.bot, title, assignee, creator_id, dl_str
    )

    status = "✅ Xabar yuborildi" if sent else "⚠️ Xabar yuborib bo'lmadi"
    await cb.message.edit_text(
        f"✅ <b>Vazifa yaratildi!</b>\n\n"
        f"📋 {title}\n"
        f"👤 {assignee['full_name']}\n"
        f"📅 {dl_fmt} | 🆔 #{task_id}\n\n{status}",
        parse_mode="HTML"
    )
    await cb.answer("✅")


@router.callback_query(F.data == "grp:no")
async def grp_cancel(cb: CallbackQuery):
    await cb.message.edit_text("❌ Bekor qilindi.")
    await cb.answer()
