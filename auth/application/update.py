from jwt.exceptions import PyJWTError

from fastapi import APIRouter, HTTPException, status

from werkzeug.security import generate_password_hash

from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError

from application.database import get_session
from application.serialized import Answer
from application.validate import GetCloudKeys
from application.auth import decode_token
from application.models import Users

router = APIRouter(prefix="/update", tags=["update"])


#! Добавление облачных ключей
@router.patch("/cloud_keys", response_model=Answer, tags=["cloud_key"])
async def update_cloud_keys(data: GetCloudKeys) -> Answer:

    try:
        payload = decode_token(data.token)
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    try:
        first_key = generate_password_hash(data.cloud_primary_key)
        second_key = generate_password_hash(data.cloud_secondary_key)
        third_key = generate_password_hash(data.cloud_third_key)

        async with get_session() as session:
            await session.execute(
                update(Users)
                .where(Users.id == int(payload["sub"]))
                .values(
                    cloud_primary_key=first_key,
                    cloud_secondary_key=second_key,
                    cloud_third_key=third_key,
                    email=data.email,
                )
            )

        return Answer(
            data={"user_id": payload["sub"], "email": data.email},
            message="Cloud keys updated successfully",
        )
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to patch userdata",
        )
