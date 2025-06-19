from fastapi import FastAPI, APIRouter

from application.serialized import Answer

from application import create_users

app = FastAPI(
    title="XIBIQ/profiles",
    version="0.0.0Beta",
)

api = APIRouter(prefix="/api/v1", tags=["api/v1"])


@api.get("/ping", response_model=Answer)
async def ping() -> Answer:
    """Health check endpoint"""
    return Answer(message="pong")


@api.get("/healthcheck")
async def healthcheck():
    """Health check endpoint"""
    return {"status": "ok"}


api.include_router(create_users.router)

app.include_router(api)
