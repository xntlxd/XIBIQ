import os
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

class Database(BaseModel):
    URI: str = os.getenv("DATABASE_URI")
    ECHO: bool = False

class Settings(BaseModel):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    database: Database = Database()

settings = Settings()