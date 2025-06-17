from jwt.exceptions import PyJWTError

from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException

from sqlalchemy import select

from application.serialized import Answer
from application.auth import decode_token, create_access_token
from application.database import get_session
from application.models import Users
from application.methods import get_access_payload
from application.validate.gettoken import get_token


router = APIRouter(prefix="/token", tags=["token"])


@router.post("/refresh", response_model=Answer, summary="Обновление токена")
async def refresh_token(token: Annotated[dict, Depends(get_token)]) -> Answer:
    try:
        payload = decode_token(token)

        if payload["typ"] != "refresh":
            return Answer(
                message="Invalid token type", status_code=status.HTTP_400_BAD_REQUEST
            )

        async with get_session() as session:
            user = await session.execute(
                select(Users).where(Users.id == int(payload["sub"]))
            )

            if not user:
                return Answer(
                    message="User not found", status_code=status.HTTP_404_NOT_FOUND
                )

            user = user.scalar()

            if user.banned:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Banned: {user.banned_reason}",
                )

        access_payload = await get_access_payload(user)

        access = create_access_token(data=access_payload, user_id=payload["sub"])

        access_payload["sub"] = payload["sub"]

        return Answer(
            data={"access": access, "account_info": access_payload},
            message="Token refreshed successfully!",
        )

    except PyJWTError:
        return Answer(message="Invalid token", status_code=status.HTTP_400_BAD_REQUEST)
