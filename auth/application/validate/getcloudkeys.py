from pydantic import BaseModel, EmailStr


class GetCloudKeys(BaseModel):
    token: str

    cloud_primary_key: str
    cloud_secondary_key: str
    cloud_third_key: str
    email: EmailStr
