from fastapi import FastAPI, APIRouter

app = FastAPI(title="XIBIQ", version="dev/0.0.1")

api = APIRouter(prefix="/api/v1", tags=["api_v1"])
app.include_router(api)
