import random
from aiogram import Router, md
from aiogram.types import Message
from aiogram.filters import Command
from database import get_session
from models import PhoneNumber
from sqlalchemy import select

router = Router()


async def generate_phone_number():
    return f"+185{random.randint(10000, 99999)}"


@router.message(Command("create"))
async def create_phone_number(message: Message):
    async with get_session() as session:
        # Check if user already has a number
        stmt = select(PhoneNumber).where(PhoneNumber.user_id == message.from_user.id)
        result = await session.execute(stmt)
        existing_number = result.scalar_one_or_none()

        if existing_number:
            message_text = md.bold(md.quote("You already have a number: ")) + md.code(
                md.quote(existing_number.phone_number)
            )
            await message.answer(message_text)
            return

        # Generate new number
        phone_number = await generate_phone_number()

        # Save to database
        new_number = PhoneNumber(
            user_id=message.from_user.id, phone_number=phone_number
        )
        session.add(new_number)
        await session.commit()

        message_text = (
            md.bold(md.quote("New number created: "))
            + md.code(md.quote(phone_number))
            + "\n"
            + md.italic(
                md.quote("If you forget your number, you can retrieve it with command ")
            )
            + "/myphone"
        )

        await message.answer(message_text)
