import os
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

bot = Bot(
    token=os.getenv("BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode="MarkdownV2"),
)
