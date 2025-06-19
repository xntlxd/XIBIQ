import uvicorn
import asyncio as asyncio

from application.create_app import app as app
from application.database import reset_database as reset_database
from application.config import settings

if __name__ == "__main__":
    asyncio.run(reset_database())
    uvicorn.run(
        "run:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD
    )
