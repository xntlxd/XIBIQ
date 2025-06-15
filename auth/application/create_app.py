from application import crud
from fastapi import FastAPI, APIRouter
from application.serialized import Answer

app = FastAPI(title="XIBIQ", version="dev/0.0.2")
api = APIRouter(prefix="/api/v1", tags=["a/v1"])


@api.get("/ping", response_model=Answer)
async def ping() -> Answer:
    return Answer(message="pong")


api.include_router(crud.router)

app.include_router(api)
