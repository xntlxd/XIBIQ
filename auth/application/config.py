import os
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


class Redis(BaseModel):
    URI: str = os.getenv("REDIS_URI")


class Taskiq(BaseModel):
    URI: str = os.getenv("RMQ_URI")


class Auth(BaseModel):
    PUBLIC_KEY_PATH: Path = Path(__file__).parent / "certs" / "public.pem"
    PRIVATE_KEY_PATH: Path = Path(__file__).parent / "certs" / "private.pem"

    PUBLIC_KEY_PATH: str | bytes = PUBLIC_KEY_PATH.read_text()
    PRIVATE_KEY_PATH: str | bytes = PRIVATE_KEY_PATH.read_text()

    ALHORITHM: str = "RS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30


class Database(BaseModel):
    URI: str = os.getenv("DATABASE_URI")
    ECHO: bool = False


class Settings(BaseModel):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    database: Database = Database()
    auth: Auth = Auth()
    taskiq: Taskiq = Taskiq()
    redis: Redis = Redis()


settings = Settings()
