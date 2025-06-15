from fastapi import FastAPI, APIRouter
from application.serialized import Answer
from application.broker import broker, lifespan
from application import crud
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="XIBIQ",
    version="dev/0.0.3",
    lifespan=lifespan,
)

api = APIRouter(prefix="/api/v1", tags=["api/v1"])


@api.get("/ping", response_model=Answer)
async def ping() -> Answer:
    """Health check endpoint"""
    return Answer(message="pong")


# Подключаем остальные роутеры
api.include_router(crud.router)

app.include_router(api)


@app.get("/taskiq")
async def taskiq_info():
    """Информация о брокере задач"""
    return {
        "broker": str(broker),
        "is_connected": broker.is_connected,
        "exchange": broker.exchange_name,
        "queue": broker.queue_name,
    }
