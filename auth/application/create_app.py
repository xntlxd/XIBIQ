import logging

from fastapi import FastAPI, APIRouter

from application import tokens
from application import authorization
from application import devroute
from application import update

from application.serialized import Answer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="XIBIQ/auth",
    version="dev/0.1.1",
)

api = APIRouter(prefix="/api/v1", tags=["api/v1"])


@api.get("/ping", response_model=Answer)
async def ping() -> Answer:
    """Health check endpoint"""
    return Answer(message="pong")


# Подключаем остальные роутеры
api.include_router(authorization.router)
api.include_router(tokens.router)
api.include_router(devroute.router)
api.include_router(update.router)

app.include_router(api)
