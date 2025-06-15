import random
import uuid
from fastapi import APIRouter, HTTPException
from application.validate import AuthUser, GetCode
from application.serialized import Answer
from datetime import datetime, timedelta, UTC

redis: list = []

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/auth/telephone", response_model=Answer)
async def auth_telephone(data: AuthUser) -> Answer:

    query_id = str(uuid.uuid4())
    telephone = data.telephone
    code = random.randint(0, 999999)
    expired: datetime = datetime.now(UTC) + timedelta(minutes=5)

    sms_query: dict = {
        "query_id": query_id,
        "telephone": telephone,
        "code": code,
        "expired": expired,
    }

    redis.append(sms_query)

    print(sms_query)

    return Answer(
        data={
            "query_id": query_id,
            "telephone": telephone,
            "expired": expired.isoformat(),
        },
        message="Code retrieved successfully, expires in five minutes!",
    )


@router.post("/auth/code", response_model=Answer)
async def auth_code(data: GetCode) -> Answer:

    print(data)

    if data.query_id is None or data.telephone is None or data.code is None:
        raise HTTPException(
            status_code=400, detail="Invalid query_id, telephone or code"
        )

    inv = HTTPException(status_code=401, detail="Invalid code")

    try:
        for row in redis:
            if (
                row["query_id"] == data.query_id
                and row["telephone"] == data.telephone
                and row["code"] == data.code
            ):
                if row["expired"] < datetime.now(UTC):
                    raise inv
                else:
                    redis.remove(row)
                    break
            else:
                raise inv
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid code")

    return Answer(
        data=data,
    )


@router.get("/auth/redis", response_model=Answer)
async def auth() -> Answer:
    return Answer(
        data=redis,
    )
