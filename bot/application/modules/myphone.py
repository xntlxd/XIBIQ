from aiogram import Router, md
from aiogram.types import Message
from aiogram.filters import Command
from application.database import get_session
from application.models import PhoneNumber
from sqlalchemy import select

router = Router()


@router.message(Command("myphone"))
async def get_my_phone(message: Message):
    async with get_session() as session:
        stmt = select(PhoneNumber).where(PhoneNumber.user_id == message.from_user.id)
        result = await session.execute(stmt)
        phone_number = result.scalar_one_or_none()

        if phone_number:
            message_text = md.bold(md.quote("Your number: ")) + md.code(
                md.quote(phone_number.phone_number)
            )
            await message.answer(message_text)
        else:
            message_text = (
                md.bold(md.quote("You don't have a number yet.\n"))
                + md.bold(md.quote("Create one with command "))
                + md.quote("/create")
            )
            await message.answer(message_text)
