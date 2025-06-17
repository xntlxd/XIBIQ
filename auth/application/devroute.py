from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException

from application.serialized import Answer
from application.redis_init import Redis, get_redis_codes
from application.validate import gen_token
from application.methods import get_access_payload
from application.auth import (
    create_access_token,
    create_refresh_token,
    create_system_token,
)

from redis.exceptions import RedisError


router = APIRouter(prefix="/dev", tags=["only/dev"])


#! Получение токена
@router.post(
    "/token", response_model=Answer, summary="Генерация токена", tags=["token"]
)
async def get_token(tokeninfo: Annotated[dict, Depends(gen_token)]):
    if tokeninfo["type"].lower() == "access" or tokeninfo["type"].lower() == "a":

        class User:
            is_admin: bool = False
            is_sudo: bool = False

        access_payload = await get_access_payload(User(), True)
        token = create_access_token(payload=access_payload, user_id=tokeninfo["sub"])
    elif tokeninfo["type"].lower() == "refresh" or tokeninfo["type"].lower() == "r":
        # token = create_refresh_token(user_id=random.randint(1, 1000))     # Рандюзер
        token = create_refresh_token(user_id=1)  # Точно существующий пользователь
    elif tokeninfo["type"].lower() == "system" or tokeninfo["type"].lower() == "s":
        token = create_system_token({"act": "all"})
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token type"
        )

    return Answer(
        data={
            "token": token,
            "input": {"type": tokeninfo["type"], "payload": tokeninfo["payload"]},
        },
        message="Token generated successfully!",
    )


#! Получение значения редис по его ключу [ОНЛИДЕВФИЧА]
@router.get("/redis", response_model=Answer, summary="РЕДИСКА")
async def get_redis_value(
    query_id: str, redis: Redis = Depends(get_redis_codes)
) -> Answer:
    """
    Получение значения ключа от редиски
    """
    try:
        if not query_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Query ID is required"
            )

        value = await redis.get(query_id)
        if not value:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Value not found"
            )

        return Answer(
            data={"value": value},
            message="Value retrieved successfully",
        )
    except RedisError as e:
        print(f"Redis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get value from Redis",
        )
