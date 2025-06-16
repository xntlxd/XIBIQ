import uvicorn
from application import settings
from application import app as app

if __name__ == "__main__":
    uvicorn.run(
        "run:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD
    )
