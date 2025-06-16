from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool
from application.config import settings


async def get_redis_client() -> Redis:
    pool = ConnectionPool.from_url(settings.redis.URI, decode_responses=True)
    return Redis(connection_pool=pool)


async def get_redis_codes() -> Redis:
    pool = ConnectionPool.from_url(settings.redis.URI + "/1", decode_responses=True)
    return Redis(connection_pool=pool)
