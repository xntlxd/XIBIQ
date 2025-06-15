import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from modules import start, generate, myphone
from database import init_db

load_dotenv()
logging.basicConfig(level=logging.INFO)


async def main():
    await init_db()

    bot = Bot(
        token=os.getenv("BOT_TOKEN"),
        default=DefaultBotProperties(parse_mode="MarkdownV2"),
    )
    disp = Dispatcher()

    disp.include_router(start.router)
    disp.include_router(generate.router)
    disp.include_router(myphone.router)

    await disp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
