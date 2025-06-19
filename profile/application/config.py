import os

from pydantic import BaseModel

from pathlib import Path


class Auth(BaseModel):
    PUBLIC_KEY_PATH: Path = Path(__file__).parent / "certs" / "public.pem"

    PUBLIC_KEY: str | bytes = PUBLIC_KEY_PATH.read_text()

    ALHORITHM: str = "RS256"


class Database(BaseModel):
    URI: str = os.getenv("PROFILE_DATABASE_URI")
    ECHO: bool = False


class Settings(BaseModel):
    HOST: str = "0.0.0.0"
    PORT: int = 8002
    RELOAD: bool = True

    database: Database = Database()
    auth: Auth = Auth()


settings = Settings()
