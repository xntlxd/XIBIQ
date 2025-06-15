import random
import uuid
from fastapi import APIRouter, Depends, HTTPException
from application.validate import AuthUser, GetCode
from application.serialized import Answer
from datetime import datetime, timedelta, UTC
from .redis_init import get_redis_client
from redis.asyncio import Redis

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/auth/telephone", response_model=Answer)
async def auth_telephone(
    data: AuthUser, redis: Redis = Depends(get_redis_client)
) -> Answer:
    query_id = str(uuid.uuid4())
    telephone = data.telephone
    code = f"{random.randint(0, 999999):06d}"  # 6 цифр с ведущими нулями
    expired = datetime.now(UTC) + timedelta(minutes=5)

    print(f"Code: {code}")

    return Answer(
        data={
            "query_id": query_id,
            "telephone": telephone,
            "expired": expired.isoformat(),
        },
        message="Code retrieved successfully, expires in five minutes!",
    )


@router.post("/auth/code", response_model=Answer)
async def auth_code(data: GetCode, redis: Redis = Depends(get_redis_client)) -> Answer:
    value = await redis.get(data.query_id)
    if not value:
        raise HTTPException(status_code=404, detail="Code expired or not found")

    telephone, code = value.split("$")

    if telephone != data.telephone or code != data.code:
        raise HTTPException(status_code=400, detail="Invalid code")

    return Answer(
        message="Code verified successfully!",
    )


@router.post("/auth/cloud_key", response_model=Answer)
async def auth_cloud_key():
    pass


@router.get("/auth/redis", response_model=Answer)
async def get_redis_value(
    query_id: str, redis: Redis = Depends(get_redis_client)
) -> Answer:
    value = await redis.get(query_id)
    if not value:
        raise HTTPException(status_code=404, detail="Value not found")

    return Answer(
        data={"value": value},
        message="Value retrieved successfully",
    )
