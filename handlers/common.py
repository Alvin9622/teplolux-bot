from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
from config import ADMIN_IDS
from keyboards.kb import lang_kb, main_kb, back_kb
from texts import T

router = Router()


class RegStates(StatesGroup):
    position = State()


def is_admin(user):
    if not user:
        return False
    return user["role"] == "admin" or user["telegram_id"] in ADMIN_IDS


async def get_lang(telegram_id):
    u = await db.get_user(telegram_id)
    return u["lang"] if u else "uz"


async def show_main(target, lang, user):
    text = T(lang, "main_menu", name=user["full_name"].split()[0])
    kb   = main_kb(lang, is_admin(user))
    if isinstance(target, Message):
        await target.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        try:
            await target.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            await target.message.answer(text, reply_markup=kb, parse_mode="HTML")


# ─── /start ──────────────────────────────────────────────────────

@router.message(Command("start"))
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    user = await db.get_user(msg.from_user.id)
    if not user:
        await msg.answer(T("uz", "welcome_new"), reply_markup=lang_kb(), parse_mode="HTML")
        return
    lang = user["lang"]
    await show_main(msg, lang, user)


# ─── /help ───────────────────────────────────────────────────────

@router.message(Command("help"))
async def cmd_help(msg: Message):
    user = await db.get_user(msg.from_user.id)
    lang = user["lang"] if user else "uz"
    admin = is_admin(user)
    text = T(lang, "help_admin") if admin else T(lang, "help_employee")
    await msg.answer(text, parse_mode="HTML", reply_markup=back_kb(lang, "main"))


@router.callback_query(F.data == "go:help")
async def go_help(cb: CallbackQuery):
    user = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(T("uz", "not_registered"), show_alert=True)
        return
    lang  = user["lang"]
    admin = is_admin(user)
    text  = T(lang, "help_admin") if admin else T(lang, "help_employee")
    try:
        await cb.message.edit_text(text, parse_mode="HTML", reply_markup=back_kb(lang, "main"))
    except Exception:
        await cb.message.answer(text, parse_mode="HTML", reply_markup=back_kb(lang, "main"))
    await cb.answer()


# ─── /cancel /bekor ──────────────────────────────────────────────

@router.message(Command("cancel"))
@router.message(Command("bekor"))
async def cmd_cancel(msg: Message, state: FSMContext):
    cur = await state.get_state()
    if cur is None:
        user = await db.get_user(msg.from_user.id)
        lang = user["lang"] if user else "uz"
        await msg.answer(T(lang, "no_active_process"))
        return
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.clear()
    user = await db.get_user(msg.from_user.id)
    await msg.answer(T(lang, "cancelled"))
    if user:
        await show_main(msg, lang, user)


# ─── Lang selection ───────────────────────────────────────────────

@router.callback_query(F.data.startswith("lang:"))
async def choose_lang(cb: CallbackQuery, state: FSMContext):
    lang = cb.data.split(":")[1]
    user = await db.get_user(cb.from_user.id)

    if not user:
        # Yangi foydalanuvchi — ro'yxatdan o'tkazish
        await state.update_data(lang=lang, tg_id=cb.from_user.id,
                                 full_name=cb.from_user.full_name or "Noma'lum",
                                 username=cb.from_user.username)
        await state.set_state(RegStates.position)
        await cb.message.edit_text(T(lang, "enter_position"), parse_mode="HTML")
    else:
        await db.update_user_lang(cb.from_user.id, lang)
        await cb.message.edit_text(T(lang, "lang_set"))
        await show_main(cb, lang, user)
    await cb.answer()


@router.message(RegStates.position)
async def reg_position(msg: Message, state: FSMContext):
    data = await state.get_data()
    lang     = data["lang"]
    tg_id    = data["tg_id"]
    name     = data["full_name"]
    username = data.get("username")
    position = msg.text.strip()

    role = "admin" if tg_id in ADMIN_IDS else "employee"
    await db.create_user(tg_id, name, username, role, lang, position)
    await state.clear()

    await msg.answer(
        T(lang, "registration_done", name=name, position=position),
        parse_mode="HTML"
    )
    user = await db.get_user(tg_id)
    await show_main(msg, lang, user)


# ─── Navigation ──────────────────────────────────────────────────

@router.callback_query(F.data == "go:main")
async def go_main(cb: CallbackQuery):
    user = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer(T("uz", "not_registered"), show_alert=True)
        return
    await show_main(cb, user["lang"], user)
    await cb.answer()


@router.callback_query(F.data == "go:lang")
async def go_lang(cb: CallbackQuery):
    lang = await get_lang(cb.from_user.id)
    await cb.message.edit_text(T(lang, "choose_lang") if "choose_lang" in __import__("texts").TEXTS[lang] else "🌐 Til:", reply_markup=lang_kb())
    await cb.answer()


# ─── Universal go: router ─────────────────────────────────────────

@router.callback_query(F.data.startswith("go:"))
async def universal_go(cb: CallbackQuery):
    dest = cb.data[3:]  # "go:task_view_3" -> "task_view_3"

    if dest == "admin:users":
        from handlers.admin import users_menu
        await users_menu(cb)
        return

    if dest == "admin:by_emp":
        from handlers.admin import by_employee
        await by_employee(cb)
        return

    if dest == "admin":
        from handlers.admin import go_admin
        await go_admin(cb)
        return

    if dest == "mytasks":
        from handlers.employee import go_mytasks
        await go_mytasks(cb)
        return

    if dest == "mystats":
        from handlers.employee import my_stats
        await my_stats(cb)
        return

    if dest == "main":
        user = await db.get_user(cb.from_user.id)
        if not user:
            await cb.answer(T("uz", "not_registered"), show_alert=True)
            return
        await show_main(cb, user["lang"], user)
        await cb.answer()
        return

    if dest.startswith("task_view_"):
        from handlers.employee import go_task_view
        await go_task_view(cb)
        return

    if dest == "rm_menu" or dest == "rm:menu":
        from handlers.roadmap import rm_menu
        await rm_menu(cb)
        return

    if dest.startswith("rm_phase_"):
        phase = dest[len("rm_phase_"):]
        from handlers.roadmap import _show_phase
        user = await db.get_user(cb.from_user.id)
        lang = user["lang"] if user else "uz"
        await _show_phase(cb, phase, lang)
        return

    if dest == "expenses":
        from handlers.expenses import expenses_menu
        await expenses_menu(cb)
        return

    if dest.startswith("admin:"):
        # admin: prefixli noma'lum yo'nalish — admin menyuga qaytamiz
        from handlers.admin import go_admin
        cb.data = "go:admin"
        await go_admin(cb)
        return

    await cb.answer()
