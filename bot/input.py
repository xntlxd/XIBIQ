import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from application.validate.get_query import GetQuery
from application.create_bot import bot
from application.serialized.answer import Answer
from application.redis_init import get_redis_client
from redis.asyncio import Redis
from application.database import get_session
from aiogram import md
from sqlalchemy import select
from application.models import PhoneNumber
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

@app.post("/auth/send_code", response_model=Answer)
async def send_code(
    data: GetQuery, 
    redis: Redis = Depends(get_redis_client),
) -> Answer:
    query_id = data.query_id
    telephone = data.telephone
    code = data.code

    message_text = (
        md.bold(md.quote("Your XIBIQ account login code is: "))
        + md.code(code) + "\n\n" 
        + md.italic(md.quote("Do not share this code with anyone.\nIf it is not you, ignore this message."))
    )

    try:
        async with get_session() as session:
        # Получаем пользователя из базы
            result = await session.execute(
                select(PhoneNumber).where(PhoneNumber.phone_number == telephone)
            )
            user = result.scalars().first()
        
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Отправляем сообщение через бота
            await bot.send_message(chat_id=user.user_id, text=message_text)

        # Сохраняем код в Redis
        await redis.set(
            name=query_id,
            value=f"{telephone}${code}",
            ex=300  # 5 минут
        )

        return Answer(
            data=data,
            message="Code sent successfully!"
        )

    except Exception as e:
        print(f"Error sending code {code} to {telephone}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send code")

if __name__ == "__main__":
    uvicorn.run(
        "input:app",
        host="127.0.0.1",
        port=8015,
        reload=True
    )