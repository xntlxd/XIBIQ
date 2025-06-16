from pydantic import BaseModel


class GetCode(BaseModel):
    query_id: str
    telephone: str
    code: str
