from fastapi import FastAPI, APIRouter
from application.serialized import Answer
from application import authorization
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="XIBIQ/auth",
    version="dev/0.1",
)

api = APIRouter(prefix="/api/v1", tags=["api/v1"])


@api.get("/ping", response_model=Answer)
async def ping() -> Answer:
    """Health check endpoint"""
    return Answer(message="pong")


# Подключаем остальные роутеры
api.include_router(authorization.router)

app.include_router(api)
