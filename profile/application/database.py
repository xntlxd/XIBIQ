from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from application.models import Base
from application.config import settings

engine = create_async_engine(url=settings.database.URI, echo=settings.database.ECHO)

AsyncSessionLocal = AsyncSession(bind=engine, expire_on_commit=False)


@asynccontextmanager
async def get_session():
    async with AsyncSessionLocal as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.commit()


async def reset_database(echo: bool = False):
    async with engine.begin() as conn:
        engine.echo = False
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        engine.echo = echo
