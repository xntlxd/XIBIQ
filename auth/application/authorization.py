import random
import uuid
import httpx
import jwt

from datetime import datetime, timedelta, UTC

from fastapi import APIRouter, Depends, HTTPException, status, Request

from jwt import PyJWTError

from application.serialized import Answer
from application.redis_init import get_redis_codes
from application.database import get_session
from application.models import Users
from application.methods import get_access_payload
from application.validate import AuthUser, GetCode, RegistrationUser, GetCloudKey
from application.auth import (
    create_access_token,
    create_refresh_token,
    create_system_token,
    decode_token,
)

from redis.asyncio import Redis
from redis.exceptions import RedisError

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from werkzeug.security import check_password_hash

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

# TODO: Сделать логику входа через облачный ключ и сделать восстановление


#! Пользователь вводит телефон и получает код
@router.post("/telephone", response_model=Answer, summary="Получение кода")
async def auth_telephone(data: AuthUser) -> Answer:
    """
    Высылает код на определенный номер!
    Номер телефона парситься до вида -> 12345678. Допуснимый номер: +1 (852) 40-42
    """
    query_id = str(uuid.uuid4())
    code = f"{random.randint(0, 999999):06d}"
    expired = datetime.now(UTC) + timedelta(minutes=5)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://127.0.0.1:8015/auth/send_code",
                json={"query_id": query_id, "telephone": data.telephone, "code": code},
                timeout=10.0,
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send SMS code",
                )

            response_data = response.json()
            if response_data.get("message") != "Code sent successfully!":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=response_data.get("detail", "Failed to send code"),
                )

        return Answer(
            data={
                "query_id": query_id,
                "telephone": data.telephone,
                "expired": expired.isoformat(),
            },
            message="Code retrieved successfully, expires in five minutes!",
        )

    except httpx.RequestError as e:
        print(f"HTTP request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SMS service unavailable",
        )
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


#! Полученный код пользователь вводит, если код верный то аккаунт либо регистрируется, либо продолжается вход
@router.post("/code", response_model=Answer, summary="Проверка кода")
async def auth_code(
    data: GetCode, request: Request, redis: Redis = Depends(get_redis_codes)
) -> Answer:
    """
    Проверка кода!
    """
    try:
        # Валидация входных данных
        if not data.query_id or not data.telephone or not data.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields",
            )

        # Получаем код из Redis
        try:
            value = await redis.get(data.query_id)
            if not value:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Code expired or not found",
                )
        except RedisError as e:
            print(f"Redis error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify code",
            )

        telephone, code = value.split("$")

        # Проверка совпадения кода
        if telephone != data.telephone or code != data.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code"
            )

        # Удаляем использованный код
        try:
            await redis.delete(data.query_id)
        except RedisError as e:
            print(f"Redis delete error: {e}")

        # Работа с базой данных
        try:
            async with get_session() as session:
                result = await session.execute(
                    select(Users).where(Users.telephone == data.telephone)
                )
                user = result.scalar()

                if not user:
                    system_token = create_system_token(data.telephone, "reg")
                    return Answer(
                        data={
                            "action": "registration",
                            "telephone": data.telephone,
                            "token": system_token,
                        },
                        message="Let's register your account!",
                    )

                if user.cloud_primary_key:
                    system_token = create_system_token(user.id, "clk")
                    return Answer(
                        data={
                            "action": "cloud_key",
                            "user_id": user.id,
                            "telephone": user.telephone,
                            "token": system_token,
                        },
                        message="Let's login your account!",
                    )

                access_payload = await get_access_payload(user)
                access_token = create_access_token(access_payload, user.id)
                refresh_token = create_refresh_token(user.id)

                user_ip = request.client.host

                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            "http://127.0.0.1:8015/new_auth",
                            json={
                                "ip": user_ip,
                                "date": int(datetime.now(UTC).timestamp()),
                                "telephone": user.telephone,
                            },
                            timeout=10.0,
                        )

                        if response.status_code != 200:
                            raise HTTPException(
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to send SMS code",
                            )
                except Exception:
                    print("Failed to send NewSession message")

                return Answer(
                    data={
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "account_info": {
                            "user_id": user.id,
                            "telephone": user.telephone,
                            "full-fledged": True,
                        },
                    },
                    message="Code verified successfully!",
                )

        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database operation failed",
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


#! Регистрация пользователя и получение токенов
@router.post("/registration", response_model=Answer, summary="Регистрация")
async def auth_registration(data: RegistrationUser):
    """
    Регистрация пользователя! *Пока не работает, тк нет микросервиса с профилем!*
    """
    try:
        # Валидация токена
        try:
            token_data = decode_token(data.token)
            if token_data.get("typ") != "system" or token_data.get("act") != "reg":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired token",
                )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed",
            )

        # Валидация данных
        if not data.first_name and not data.last_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one name field is required",
            )

        # Создание пользователя
        try:
            async with get_session() as session:
                existing_user = await session.execute(
                    select(Users).where(Users.telephone == data.telephone)
                )
                if existing_user.scalar():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="User already exists",
                    )

                user = Users(telephone=data.telephone)
                session.add(user)
                await session.commit()
                await session.refresh(user)

                # TODO: Сделать создание профиля

                access_payload = {"ffl": True, "telephone": user.telephone}
                access_token = create_access_token(access_payload, user.id)
                refresh_token = create_refresh_token(user.id)

                return Answer(
                    data={
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "account_info": {
                            "user_id": user.id,
                            "telephone": user.telephone,
                            "full-fledged": True,
                        },
                    },
                    message="Registration successful!",
                )
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user",
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# TODO: Сделать вход по облачному ключу [inpr]
#! Получение токена по облачному ключу
@router.post(
    "/cloud_key", response_model=Answer, summary="Облачный пароль", tags=["cloud_key"]
)
async def auth_cloud_key(data: GetCloudKey):
    try:
        payload = decode_token(data.token)

        if payload.get("typ") != "system" or payload.get("act") != "clk":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token",
            )

    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed",
        )

    try:
        async with get_session() as session:
            result = await session.execute(
                select(Users).where(Users.id == data.user_id)
            )
            user = result.scalar()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            if not check_password_hash(user.cloud_primary_key, data.cloud_key):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid cloud key",
                )

            access_payload = await get_access_payload(user)
            access_token = create_access_token(access_payload, user.id)
            refresh_token = create_refresh_token(user.id)

            return Answer(
                data={
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "account_info": {
                        "user_id": user.id,
                        "telephone": user.telephone,
                        "full-fledged": True,
                    },
                },
                message="Cloud key verified successfully!",
            )
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify cloud key",
        )
