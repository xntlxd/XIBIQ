import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class DatabaseSettings(BaseModel):
    URI: str = os.getenv("DATABASE_URI")
    ECHO: bool = False


class Settings(BaseModel):
    database: DatabaseSettings = DatabaseSettings()


settings = Settings()
