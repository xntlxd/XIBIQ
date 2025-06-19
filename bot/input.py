import uvicorn

from datetime import datetime, UTC

from fastapi import FastAPI, Depends, HTTPException

from application.validate import GetQuery, NewAuth
from application.create_bot import bot
from application.serialized.answer import Answer
from application.redis_init import get_redis_codes
from application.database import get_session
from application.models import PhoneNumber
from application.methods import get_location_by_ip

from redis.asyncio import Redis

from aiogram import md

from sqlalchemy import select

app = FastAPI(
    title="XIBIQ/tgbot",
    version="bot/0.1.1",
)


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.origins.allow_origins,
# )


@app.post("/auth/send_code", response_model=Answer)
async def send_code(
    data: GetQuery,
    redis: Redis = Depends(get_redis_codes),
) -> Answer:
    query_id = data.query_id
    telephone = data.telephone
    code = data.code

    message_text = (
        md.bold(md.quote("Your XIBIQ account login code is: "))
        + md.code(code)
        + "\n\n"
        + md.italic(
            md.quote(
                "❗️Do not share this code with anyone.\nIf it is not you, ignore this message."
            )
        )
    )

    try:
        async with get_session() as session:
            result = await session.execute(
                select(PhoneNumber).where(PhoneNumber.phone_number == telephone)
            )
            user = result.scalars().first()

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Отправляем сообщение через бота
            await bot.send_message(chat_id=user.user_id, text=message_text)

        # Сохраняем код в Redis
        await redis.set(name=query_id, value=f"{telephone}${code}", ex=300)  # 5 минут

        return Answer(data=data, message="Code sent successfully!")

    except Exception as e:
        print(f"Error sending code {code} to {telephone}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send code")


@app.post("/auth/new_auth", response_model=Answer)
async def new_auth(
    data: NewAuth,
    redis: Redis = Depends(get_redis_codes),
) -> Answer:
    date: datetime = datetime.fromtimestamp(data.date, UTC)

    if data.ip != "127.0.0.1":
        location_info = await get_location_by_ip(data.ip)
        location = f"{location_info["city"]} - {location_info["country"]}[{data.ip}]"
    else:
        location = f"Localhost[{data.ip}]"

    message_text = md.bold(md.quote("New login to your account!")) + md.italic(
        md.quote(f"\nWith {location} at {date.strftime("%d %B %Y - %H:%M")}.")
    )

    try:
        async with get_session() as session:
            result = await session.execute(
                select(PhoneNumber).where(PhoneNumber.phone_number == data.telephone)
            )
            user = result.scalar()

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            await bot.send_message(chat_id=user.user_id, text=message_text)

        return Answer(data=data, message="Message sent successfully!")

    except Exception as e:
        print(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send code")


if __name__ == "__main__":
    uvicorn.run("input:app", host="0.0.0.0", port=8015, reload=True)
