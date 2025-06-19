import jwt
import uuid

from application.config import settings

from datetime import datetime, timedelta, UTC


def create_access_token(payload: dict | None = None, user_id: int | str | None = None):
    header = {"alg": "RS256", "typ": "JWT"}

    if payload is None:
        payload = {}
    else:
        acsess_payload = payload.copy()

    if "sub" not in acsess_payload and user_id:
        acsess_payload["sub"] = str(user_id)
    elif "sub" in payload:
        acsess_payload["sub"] = str(acsess_payload["sub"])

    NOW = datetime.now(UTC)
    EXP = NOW + timedelta(minutes=settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES)

    acsess_payload["iat"] = NOW.timestamp()
    acsess_payload["nbf"] = NOW.timestamp()
    acsess_payload["exp"] = EXP.timestamp()
    acsess_payload["jti"] = str(uuid.uuid4())
    acsess_payload["typ"] = "access"  # :typ - тип токена

    return jwt.encode(
        payload=acsess_payload,
        key=settings.auth.PRIVATE_KEY,
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
        key=settings.auth.PRIVATE_KEY,
        algorithm=settings.auth.ALHORITHM,
        headers=header,
    )


def create_system_token(
    user_id: int | str, action: str | None = None, data: dict | None = None
):
    NOW = datetime.now(UTC)
    EXP = NOW + timedelta(minutes=settings.auth.SYSTEM_TOKEN_EXPIRE_MINUTES)

    header = {"alg": "RS256", "typ": "JWT"}
    payload = data if data is not None else {}

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
        key=settings.auth.PRIVATE_KEY,
        algorithm=settings.auth.ALHORITHM,
        headers=header,
    )


def decode_token(token: str):
    data = jwt.decode(
        jwt=token,
        key=settings.auth.PUBLIC_KEY,
        algorithms=[settings.auth.ALHORITHM],
    )
    return data
