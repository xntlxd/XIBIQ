from datetime import datetime, timedelta

from aiogram import Router, F, md
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from application.database import get_session
from application.models import PhoneNumber

from sqlalchemy import delete

router = Router()


class DeleteStates(StatesGroup):
    AWAITING_CONFIRMATION = State()


@router.message(Command("delete"))
async def start_delete_process(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Confirm Deletion", callback_data="confirm_delete")
    builder.button(text="❌ Cancel", callback_data="cancel_delete")

    await state.set_state(DeleteStates.AWAITING_CONFIRMATION)
    await state.set_data(
        {
            "expires_at": datetime.now() + timedelta(minutes=5),
            "user_id": message.from_user.id,
        }
    )

    await message.answer(
        "⚠️ Are you sure you want to delete your phone number?",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(DeleteStates.AWAITING_CONFIRMATION, F.data == "confirm_delete")
async def confirm_delete(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    # Check if session expired
    if datetime.now() > data["expires_at"]:
        await callback.message.edit_text(
            md.bold(md.quote("⌛ Session expired. Please start over."))
        )
        await state.clear()
        return

    async with get_session() as session:
        stmt = delete(PhoneNumber).where(PhoneNumber.user_id == callback.from_user.id)
        await session.execute(stmt)
        await session.commit()

    await state.clear()
    await callback.message.edit_text(
        md.bold(md.quote("✅ Phone number deleted successfully."))
    )
    await callback.answer()


@router.callback_query(DeleteStates.AWAITING_CONFIRMATION, F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        md.bold(md.quote("❌ Operation canceled. Your phone number remains unchanged."))
    )
    await callback.answer()


@router.callback_query(DeleteStates.AWAITING_CONFIRMATION)
async def handle_unknown_callbacks(callback: CallbackQuery):
    await callback.answer("⚠️ Invalid action", show_alert=True)
