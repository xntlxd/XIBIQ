from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from config import settings
from contextlib import asynccontextmanager
from models import Base

# Важно создать engine только один раз
engine = None
AsyncSessionLocal = None


async def init_db():
    global engine, AsyncSessionLocal
    engine = create_async_engine(url=settings.database.URI, echo=settings.database.ECHO)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    # Создаем таблицы при инициализации
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def get_session():
    if AsyncSessionLocal is None:
        await init_db()
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def reset_database(echo: bool = False):
    if engine is None:
        await init_db()
    async with engine.begin() as conn:
        engine.echo = False
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        engine.echo = echo
