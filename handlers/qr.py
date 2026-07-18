"""QR kod generatori: havola/matn → PNG QR kod."""
import io
import logging

import qrcode
from qrcode.constants import ERROR_CORRECT_M

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, BufferedInputFile

import database as db
from keyboards.kb import back_kb
from texts import T

logger = logging.getLogger(__name__)
router = Router()


class QRStates(StatesGroup):
    waiting_input = State()


def _make_qr_png(data: str) -> bytes:
    """Matn/havoladan QR kod PNG bytes qaytaradi."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@router.callback_query(F.data == "go:qr")
async def qr_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    user = await db.get_user(cb.from_user.id)
    if not user:
        await cb.answer("Avval /start bosing", show_alert=True)
        return
    lang = user.get("lang", "uz")
    await state.set_state(QRStates.waiting_input)
    await cb.message.edit_text(
        T(lang, "qr_ask_input"),
        reply_markup=back_kb(lang, "main"),
        parse_mode="HTML",
    )
    await cb.answer()


@router.message(QRStates.waiting_input)
async def qr_generate(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user.get("lang", "uz") if user else "uz"

    data = (message.text or "").strip()
    if not data:
        await message.answer(T(lang, "qr_invalid"))
        return
    if len(data) > 1500:
        await message.answer(T(lang, "qr_too_long"))
        return

    try:
        png = _make_qr_png(data)
    except Exception as e:
        logger.error("QR generate error: %s", e)
        await message.answer(T(lang, "error"))
        return

    preview = data if len(data) <= 100 else data[:100] + "…"
    photo = BufferedInputFile(png, filename="qrcode.png")
    await message.answer_photo(
        photo=photo,
        caption=T(lang, "qr_done").format(data=preview),
        parse_mode="HTML",
    )
    # Holat saqlanadi — foydalanuvchi yana havola yuborishi mumkin
    await message.answer(
        T(lang, "qr_again"),
        reply_markup=back_kb(lang, "main"),
        parse_mode="HTML",
    )
