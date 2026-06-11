from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from config import ADMIN_IDS, GROUP_ID
from keyboards.kb import tasks_list_kb, task_actions_kb, status_kb, back_kb
from texts import T, status_txt
from utils.formatters import task_card, progress_bar, employee_monthly_report

router = Router()


class EmpStates(StatesGroup):
    cancel_reason = State()
    progress      = State()
    upload_file   = State()
    comment       = State()


def is_admin(user):
    return user and (user["role"] == "admin" or user["telegram_id"] in ADMIN_IDS)


@router.message(Command("mytasks"))
async def cmd_mytasks(msg: Message):
    user = await db.get_user(msg.from_user.id)
    if not user:
        await msg.answer(T("uz", "not_registered"))
        return
    lang  = user["lang"]
    tasks = await db.get_tasks_for_user(user["id"])
    if not tasks:
        await msg.answer(T(lang, "no_tasks"), reply_markup=back_kb(lang, "main"), parse_mode="HTML")
        return
    await msg.answer(
        f"📋 <b>{T(lang, 'btn_my_tasks')}</b> — {len(tasks)} ta:",
        reply_markup=tasks_list_kb(lang, tasks, is_admin=False, back_to="main"),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "go:mytasks")
async def go_mytasks(cb: CallbackQuery):
    user = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(T("uz", "not_registered"), show_alert=True)
        return
    lang  = user["lang"]
    tasks = await db.get_tasks_for_user(user["id"])
    text  = f"📋 <b>{T(lang, 'btn_my_tasks')}</b> — {len(tasks)} ta:" if tasks else T(lang, "no_tasks")
    kb    = tasks_list_kb(lang, tasks, is_admin=False, back_to="main") if tasks else back_kb(lang, "main")
    try:
        await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await cb.message.answer(text, reply_markup=kb, parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("task:view:"))
async def view_task(cb: CallbackQuery):
    task_id = int(cb.data.split(":")[2])
    user    = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(T("uz", "not_registered"), show_alert=True)
        return
    lang = user["lang"]
    task = await db.get_task(task_id)
    if not task:
        await cb.answer(T(lang, "error"), show_alert=True)
        return
    admin = is_admin(user)
    if task["assignee_id"] != user["id"] and not admin:
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    assignee      = await db.get_user_by_id(task["assignee_id"])
    aname         = assignee["full_name"] if assignee else "—"
    files         = await db.get_task_files(task_id)
    comments      = await db.get_comments(task_id)
    text          = task_card(task, lang, aname, len(files), len(comments))
    is_mine       = task["assignee_id"] == user["id"]
    can_edit      = is_mine and task["status"] not in ("done","cancelled")
    back_to       = "mytasks" if is_mine else "admin:by_emp"
    try:
        await cb.message.edit_text(
            text,
            reply_markup=task_actions_kb(lang, task_id, is_mine=can_edit, is_admin=admin, back_to=back_to),
            parse_mode="HTML"
        )
    except Exception:
        await cb.message.answer(
            text,
            reply_markup=task_actions_kb(lang, task_id, is_mine=can_edit, is_admin=admin, back_to=back_to),
            parse_mode="HTML"
        )
    await cb.answer()


@router.callback_query(F.data.startswith("task:status:"))
async def ask_status(cb: CallbackQuery):
    task_id = int(cb.data.split(":")[2])
    user    = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer()
        return
    lang = user["lang"]
    task = await db.get_task(task_id)
    if not task or (task["assignee_id"] != user["id"] and not is_admin(user)):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    await cb.message.edit_text(
        f"📋 <b>{task['title']}</b>\n\n{T(lang, 'ask_status')}",
        reply_markup=status_kb(lang, task_id), parse_mode="HTML"
    )
    await cb.answer()


@router.callback_query(F.data.startswith("setstatus:"))
async def set_status(cb: CallbackQuery, state: FSMContext):
    _, task_id_s, new_status = cb.data.split(":")
    task_id = int(task_id_s)
    user    = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer()
        return
    lang = user["lang"]
    task = await db.get_task(task_id)
    if not task or (task["assignee_id"] != user["id"] and not is_admin(user)):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    if new_status == "cancelled":
        await state.update_data(task_id=task_id, old_status=task["status"],
                                 user_db_id=user["id"], lang=lang)
        await state.set_state(EmpStates.cancel_reason)
        await cb.message.edit_text(
            T(lang, "ask_cancel_reason", cancel=T(lang, "cancel_action")), parse_mode="HTML"
        )
        await cb.answer()
        return
    await db.update_task_status(task_id, new_status, user_id=user["id"], old_status=task["status"])
    await _notify_admins(cb.bot, task, new_status, user["full_name"])
    await cb.message.edit_text(
        T(lang, "status_updated", status=status_txt(lang, new_status)),
        reply_markup=back_kb(lang, "mytasks"), parse_mode="HTML"
    )
    await cb.answer("✅")


@router.message(EmpStates.cancel_reason)
async def recv_cancel_reason(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    lang    = data["lang"]
    task_id = data["task_id"]
    reason  = msg.text.strip()
    await db.update_task_status(task_id, "cancelled", cancel_reason=reason,
                                 user_id=data["user_db_id"], old_status=data["old_status"])
    task = await db.get_task(task_id)
    user = await db.get_user(msg.from_user.id)
    await _notify_admins(msg.bot, task, "cancelled", user["full_name"] if user else "?", reason)
    await msg.answer(
        T(lang, "status_updated", status=status_txt(lang, "cancelled")) + f"\n💬 {reason}",
        reply_markup=back_kb(lang, "mytasks"), parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("task:progress:"))
async def ask_progress(cb: CallbackQuery, state: FSMContext):
    task_id = int(cb.data.split(":")[2])
    user    = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer()
        return
    lang = user["lang"]
    task = await db.get_task(task_id)
    if not task or (task["assignee_id"] != user["id"] and not is_admin(user)):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    await state.update_data(task_id=task_id, user_db_id=user["id"], lang=lang)
    await state.set_state(EmpStates.progress)
    await cb.message.answer(
        T(lang, "ask_progress", cancel=T(lang, "cancel_action")), parse_mode="HTML"
    )
    await cb.answer()


@router.message(EmpStates.progress)
async def recv_progress(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    try:
        pct = int(msg.text.strip())
        if not 0 <= pct <= 100:
            raise ValueError
    except ValueError:
        await msg.answer(T(lang, "invalid_pct"))
        return
    await state.clear()
    await db.update_task_progress(data["task_id"], pct, data["user_db_id"])

    task = await db.get_task(data["task_id"])
    user = await db.get_user_by_id(data["user_db_id"])
    if task and user:
        notif = (
            f"📊 <b>Foiz yangilandi</b>\n\n"
            f"📋 {task['title']}\n"
            f"👤 {user['full_name']}\n"
            f"📈 {pct}%\n"
            f"{progress_bar(pct)}"
        )
        targets = list(ADMIN_IDS)
        if GROUP_ID:
            targets.append(GROUP_ID)
        for target in targets:
            try:
                await msg.bot.send_message(target, notif, parse_mode="HTML")
            except Exception:
                pass

    await msg.answer(
        T(lang, "progress_updated", pct=pct) + f"\n{progress_bar(pct)}",
        reply_markup=back_kb(lang, "mytasks"), parse_mode="HTML"
    )


# ─── FILE UPLOAD ─────────────────────────────────────────────────

@router.callback_query(F.data.startswith("task:upload:"))
async def ask_upload(cb: CallbackQuery, state: FSMContext):
    task_id = int(cb.data.split(":")[2])
    user    = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer()
        return
    lang = user["lang"]
    task = await db.get_task(task_id)
    if not task or (task["assignee_id"] != user["id"] and not is_admin(user)):
        await cb.answer(T(lang, "no_permission"), show_alert=True)
        return
    await state.update_data(task_id=task_id, user_db_id=user["id"], lang=lang)
    await state.set_state(EmpStates.upload_file)
    text = (
        "📎 <b>Fayl yuborish</b>\n\nRasm, video yoki hujjat yuboring.\n\n⬅️ Bekor: /bekor"
        if lang=="uz" else
        "📎 <b>Загрузить файл</b>\n\nОтправьте фото, видео или документ.\n\n⬅️ Отмена: /bekor"
    )
    await cb.message.answer(text, parse_mode="HTML")
    await cb.answer()


@router.message(EmpStates.upload_file, F.photo | F.video | F.document | F.audio)
async def recv_file(msg: Message, state: FSMContext):
    data    = await state.get_data()
    await state.clear()
    lang    = data["lang"]
    task_id = data["task_id"]
    user_id = data["user_db_id"]
    caption = msg.caption or ""
    if msg.photo:
        file_id, ft = msg.photo[-1].file_id, "photo"
    elif msg.video:
        file_id, ft = msg.video.file_id, "video"
    elif msg.document:
        file_id, ft = msg.document.file_id, "document"
    elif msg.audio:
        file_id, ft = msg.audio.file_id, "audio"
    else:
        await msg.answer("❌ Fayl turi qabul qilinmadi.")
        return
    await db.save_task_file(task_id, user_id, file_id, ft, caption)
    task = await db.get_task(task_id)
    user = await db.get_user_by_id(user_id)
    icon = {"photo":"📸","video":"🎥","document":"📄","audio":"🎵"}.get(ft,"📎")
    notif = f"{icon} <b>Yangi fayl!</b>\n\n📋 {task['title']}\n👤 {user['full_name'] if user else '?'}"
    if caption:
        notif += f"\n💬 {caption}"

    targets = list(ADMIN_IDS)
    if GROUP_ID:
        targets.append(GROUP_ID)

    for target in targets:
        try:
            await msg.bot.send_message(target, notif, parse_mode="HTML")
            if ft=="photo":      await msg.bot.send_photo(target, file_id)
            elif ft=="video":    await msg.bot.send_video(target, file_id)
            elif ft=="document": await msg.bot.send_document(target, file_id)
            elif ft=="audio":    await msg.bot.send_audio(target, file_id)
        except Exception:
            pass
    await msg.answer(
        "✅ Fayl yuklandi!" if lang=="uz" else "✅ Файл загружен!",
        reply_markup=back_kb(lang, "mytasks"), parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("task:files:"))
async def view_files(cb: CallbackQuery):
    task_id = int(cb.data.split(":")[2])
    user    = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer()
        return
    files = await db.get_task_files(task_id)
    if not files:
        await cb.answer("📭 Fayl yo'q", show_alert=True)
        return
    await cb.answer()
    for f in files:
        icon = {"photo":"📸","video":"🎥","document":"📄","audio":"🎵"}.get(f["file_type"],"📎")
        cap  = f"{icon} {f['full_name']} | {f['created_at'][:10]}"
        if f.get("caption"):
            cap += f"\n💬 {f['caption']}"
        try:
            ft = f["file_type"]
            if ft=="photo":    await cb.message.answer_photo(f["file_id"], caption=cap)
            elif ft=="video":  await cb.message.answer_video(f["file_id"], caption=cap)
            elif ft=="document": await cb.message.answer_document(f["file_id"], caption=cap)
            elif ft=="audio":  await cb.message.answer_audio(f["file_id"], caption=cap)
        except Exception:
            pass


# ─── COMMENTS ────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("task:comment:"))
async def ask_comment(cb: CallbackQuery, state: FSMContext):
    task_id = int(cb.data.split(":")[2])
    user    = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer()
        return
    lang = user["lang"]
    await state.update_data(task_id=task_id, user_db_id=user["id"], lang=lang)
    await state.set_state(EmpStates.comment)
    await cb.message.answer(
        "💬 Izohingizni yozing:\n\n⬅️ Bekor: /bekor" if lang=="uz" else
        "💬 Напишите комментарий:\n\n⬅️ Отмена: /bekor",
        parse_mode="HTML"
    )
    await cb.answer()


@router.message(EmpStates.comment)
async def recv_comment(msg: Message, state: FSMContext):
    data    = await state.get_data()
    await state.clear()
    lang    = data["lang"]
    task_id = data["task_id"]
    user_id = data["user_db_id"]
    await db.add_comment(task_id, user_id, msg.text.strip())
    task = await db.get_task(task_id)
    user = await db.get_user_by_id(user_id)
    notif = f"💬 <b>Yangi izoh</b>\n\n📋 {task['title']}\n👤 {user['full_name'] if user else '?'}\n\n{msg.text}"

    targets = list(ADMIN_IDS)
    if GROUP_ID:
        targets.append(GROUP_ID)

    for target in targets:
        try:
            await msg.bot.send_message(target, notif, parse_mode="HTML")
        except Exception:
            pass
    await msg.answer(
        "✅ Izoh qo'shildi!" if lang=="uz" else "✅ Комментарий добавлен!",
        reply_markup=back_kb(lang, f"task_view_{task_id}"), parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("task:comments:"))
async def view_comments(cb: CallbackQuery):
    task_id  = int(cb.data.split(":")[2])
    user     = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer()
        return
    comments = await db.get_comments(task_id)
    if not comments:
        await cb.answer("💬 Izoh yo'q", show_alert=True)
        return
    await cb.answer()
    lang = user["lang"]
    text = "💬 <b>Izohlar:</b>\n\n"
    for c in comments:
        text += f"👤 <b>{c['full_name']}</b> | {c['created_at'][:10]}\n{c['text']}\n\n"
    await cb.message.answer(text, parse_mode="HTML", reply_markup=back_kb(lang, f"task_view_{task_id}"))


# ─── MY STATS ────────────────────────────────────────────────────

@router.callback_query(F.data == "go:mystats")
async def my_stats(cb: CallbackQuery):
    import datetime
    user = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer()
        return
    lang  = user["lang"]
    now   = datetime.datetime.now()
    tasks = await db.get_employee_monthly_report(user["id"], now.month, now.year)
    text  = employee_monthly_report(user, tasks, now.month, now.year, lang)
    try:
        await cb.message.edit_text(text, reply_markup=back_kb(lang, "main"), parse_mode="HTML")
    except Exception:
        await cb.message.answer(text, reply_markup=back_kb(lang, "main"), parse_mode="HTML")
    await cb.answer()


async def _notify_admins(bot, task, new_status, changer_name, cancel_reason=None):
    from config import GROUP_ID
    icon = {"new":"🆕","in_progress":"🔄","done":"✅","cancelled":"❌","review":"👀"}.get(new_status,"📌")
    text = (
        f"{icon} <b>Vazifa holati o'zgardi</b>\n\n"
        f"📋 <b>{task['title']}</b>\n"
        f"👤 O'zgartirdi: {changer_name}\n"
        f"🔄 {status_txt('uz', new_status)}\n"
    )
    if cancel_reason:
        text += f"💬 {cancel_reason}\n"
    text += f"🆔 #{task['id']}"
    for aid in ADMIN_IDS:
        try:
            await bot.send_message(aid, text, parse_mode="HTML")
        except Exception:
            pass
    if GROUP_ID:
        try:
            await bot.send_message(GROUP_ID, text, parse_mode="HTML")
        except Exception:
            pass


@router.callback_query(F.data.startswith("go:task_view_"))
async def go_task_view(cb: CallbackQuery):
    task_id = int(cb.data.split("_")[-1])
    cb.data = f"task:view:{task_id}"
    await view_task(cb)
