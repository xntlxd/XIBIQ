import uvicorn
import asyncio
from application import reset_database, settings
from application import app as app

if __name__ == "__main__":
    asyncio.run(reset_database(settings.database.ECHO))
    uvicorn.run(
        "run:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD
    )
