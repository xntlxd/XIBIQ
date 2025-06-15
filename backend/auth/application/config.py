import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Database(BaseModel):
    URI: str = os.getenv("DATABASE_URI")
    FUTURE: bool = True
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 20
    POOL_PRE_PING: bool = True
    ECHO: bool = False


class Settings(BaseModel):
    database: Database = Database()


settings = Settings()
