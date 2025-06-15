import uvicorn
import asyncio
from application.database import reset_database
from application import settings


if __name__ == "__main__":
    asyncio.run(reset_database(settings.database.ECHO))
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)
