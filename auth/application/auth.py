import jwt
import uuid
from datetime import datetime, timedelta, UTC
from application.config import settings


def create_access_token(data: dict, user_id: int | str | None = None):
    NOW = datetime.now(UTC)
    EXP = NOW + timedelta(minutes=settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES)

    header = {"alg": "RS256", "typ": "JWT"}

    payload = data.copy()

    if "sub" not in payload and user_id:
        payload["sub"] = str(user_id)
    elif "sub" in payload:
        payload["sub"] = str(payload["sub"])

    payload["iat"] = NOW.timestamp()
    payload["nbf"] = NOW.timestamp()
    payload["exp"] = EXP.timestamp()
    payload["jti"] = str(uuid.uuid4())
    payload["typ"] = "access"

    return jwt.encode(
        payload=payload,
        key=settings.auth.PRIVATE_KEY_PATH,
        algorithm=settings.auth.ALHORITHM,
        headers=header,
    )


def create_refresh_token(user_id: int | str):
    NOW = datetime.now(UTC)
    EXP = NOW + timedelta(minutes=settings.auth.REFRESH_TOKEN_EXPIRE_MINUTES)

    header = {"alg": "RS256", "typ": "JWT"}
    payload = {}

    if isinstance(user_id, int):
        payload["sub"] = str(user_id)

    payload["iat"] = NOW.timestamp()
    payload["nbf"] = NOW.timestamp()
    payload["exp"] = EXP.timestamp()
    payload["jti"] = str(uuid.uuid4())
    payload["typ"] = "refresh"

    return jwt.encode(
        payload=payload,
        key=settings.auth.PRIVATE_KEY_PATH,
        algorithm=settings.auth.ALHORITHM,
        headers=header,
    )


def create_system_token(user_id: int | str, action: str | None = None):
    NOW = datetime.now(UTC)
    EXP = NOW + timedelta(minutes=settings.auth.SYSTEM_TOKEN_EXPIRE_MINUTES)

    header = {"alg": "RS256", "typ": "JWT"}
    payload = {}

    if isinstance(user_id, int):
        payload["sub"] = str(user_id)

    payload["iat"] = NOW.timestamp()
    payload["nbf"] = NOW.timestamp()
    payload["exp"] = EXP.timestamp()
    payload["jti"] = str(uuid.uuid4())
    payload["typ"] = "system"
    payload["act"] = action

    return jwt.encode(
        payload=payload,
        key=settings.auth.PRIVATE_KEY_PATH,
        algorithm=settings.auth.ALHORITHM,
        headers=header,
    )


def decode_token(token: str):
    data = jwt.decode(
        jwt=token,
        key=settings.auth.PUBLIC_KEY_PATH,
        algorithms=[settings.auth.ALHORITHM],
    )
    return data
