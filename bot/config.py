import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Taskiq(BaseModel):
    URI: str = os.getenv("RABBITMQ_URI")


class Redis(BaseModel):
    URI: str = os.getenv("REDIS_URI")


class DatabaseSettings(BaseModel):
    URI: str = os.getenv("DATABASE_URI")
    ECHO: bool = False


class Settings(BaseModel):
    database: DatabaseSettings = DatabaseSettings()
    taskiq: Taskiq = Taskiq()
    redis: Redis = Redis()


settings = Settings()
