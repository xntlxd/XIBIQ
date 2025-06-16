import asyncio
import logging
from aiogram import Dispatcher
from dotenv import load_dotenv
from application.modules import start, generate, myphone, delete
from application.database import init_db
from application.create_bot import bot

load_dotenv()
logging.basicConfig(level=logging.INFO)


async def main():
    await init_db()

    disp = Dispatcher()

    disp.include_router(start.router)
    disp.include_router(generate.router)
    disp.include_router(myphone.router)
    disp.include_router(delete.router)

    await disp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
