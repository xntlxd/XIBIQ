import random
import uuid
import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from application.validate import AuthUser, GetCode, RegistrationUser
from application.serialized import Answer
from datetime import datetime, timedelta, UTC
from application.redis_init import get_redis_codes
from redis.asyncio import Redis
from redis.exceptions import RedisError
from application.database import get_session
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from application.models import Users
from application.auth import (
    create_access_token,
    create_refresh_token,
    create_system_token,
    decode_token,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

# TODO: Сделать логику входа через облачный ключ и сделать восстановление


#! Пользователь вводит телефон и получает код
@router.post("/auth/telephone", response_model=Answer, summary="Получение кода")
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
@router.post("/auth/code", response_model=Answer, summary="Проверка кода")
async def auth_code(data: GetCode, redis: Redis = Depends(get_redis_codes)) -> Answer:
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

                access_payload = {"full-fledged": True, "telephone": user.telephone}
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
@router.post("/auth/registration", response_model=Answer, summary="Регистрация")
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
                # Проверяем, не зарегистрирован ли уже пользователь
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

                access_payload = {"full-fledged": True, "telephone": user.telephone}
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


# TODO: Сделать вход по облачному ключу
#! Получение токена по облачному ключу
@router.post("auth/cloud_key")
async def auth_cloud_key():
    pass


#! Получение значения редис по его ключу [ОНЛИДЕВФИЧА]
@router.get("/auth/redis", response_model=Answer, summary="РЕДИСКА", tags=["only/dev"])
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
