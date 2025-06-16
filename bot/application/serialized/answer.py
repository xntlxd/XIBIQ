from pydantic import BaseModel


class Answer(BaseModel):
    data: dict | list | None = None
    message: str | None = None
