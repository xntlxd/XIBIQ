from pydantic import BaseModel


class GetCloudKey(BaseModel):
    token: str
    user_id: int
    cloud_key: str
