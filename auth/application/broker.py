from taskiq_aio_pika import AioPikaBroker
from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from contextlib import asynccontextmanager
from .config import settings
import logging

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomAioPikaBroker(AioPikaBroker):
    async def startup(self) -> None:
        """Кастомная инициализация брокера"""
        try:
            await super().startup()
            logger.info("Broker connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Broker connection failed: {e}")
            raise


# Инициализация брокера
broker = CustomAioPikaBroker(
    url=settings.taskiq.URI,
    exchange_name="taskiq_exchange",
    queue_name="taskiq_queue",
    routing_key="taskiq",
)

# Инициализация планировщика
scheduler = TaskiqScheduler(broker=broker, sources=[LabelScheduleSource(broker)])


@asynccontextmanager
async def lifespan(app):
    """Lifespan для управления жизненным циклом брокера"""
    try:
        await broker.startup()
        logger.info("Broker started successfully")
        yield
    except Exception as e:
        logger.error(f"Broker startup error: {e}")
        raise
    finally:
        await broker.shutdown()
        logger.info("Broker shutdown complete")
