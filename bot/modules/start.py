from aiogram import Router, md
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command("start"))
async def start(message: Message):
    message_text = (
        md.bold(md.quote("Hello, this is XIBIQ bot!\n\n"))
        + "/create"
        + md.italic(md.quote(" - generate authorization number\n"))
        + "/myphone"
        + md.italic(md.quote(" - view your authorization number\n"))
        + "/delete"
        + md.italic(md.quote(" - delete your authorization number\n"))
    )
    await message.answer(message_text)


@router.message(Command("ping"))
async def ping(message: Message):
    await message.answer(md.quote("pong!"))
