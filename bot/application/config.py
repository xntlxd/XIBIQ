import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Origins(BaseModel):
    allow_ports: list[int] = [8001]

    allow_origins: list[str] = [f"http://localhost:{port}" for port in allow_ports]


class Redis(BaseModel):
    URI: str = os.getenv("REDIS_URI")


class DatabaseSettings(BaseModel):
    URI: str = os.getenv("BOT_DATABASE_URI")
    ECHO: bool = False


class Settings(BaseModel):
    database: DatabaseSettings = DatabaseSettings()
    redis: Redis = Redis()
    origins: Origins = Origins()


settings = Settings()
