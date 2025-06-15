import re
from .tuned import TunedModel
from pydantic import BaseModel, EmailStr, field_validator


class LoginUser(BaseModel):
    telephone: str

    cloud_primary_key: str | None

    @field_validator("telephone")
    def validate_telephone(cls, value: str | None) -> str | None:
        if not value:
            return None

        cleaned_number = re.sub(r"[^\d]", "", value)

        if not cleaned_number:
            raise ValueError("Phone number cannot be empty after cleaning")

        if not cleaned_number.isdigit():
            raise ValueError("Phone number must contain only digits")

        if len(cleaned_number) < 10:
            raise ValueError("Phone number must be at less than 10 digits long")

        return cleaned_number


class ShowUser(TunedModel):
    id: int
    telephone: str
    email: EmailStr
