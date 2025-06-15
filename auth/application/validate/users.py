import re
from pydantic import BaseModel, field_validator, EmailStr


class AuthUser(BaseModel):
    telephone: str

    @field_validator("telephone")
    def validate_telephone(cls, value: str | None) -> str | None:
        if not value:
            return None

        cleaned_number = re.sub(r"[^\d]", "", value)

        if not cleaned_number:
            raise ValueError("Phone number cannot be empty after cleaning")

        if not cleaned_number.isdigit():
            raise ValueError("Phone number must contain only digits")

        if len(cleaned_number) < 8:
            raise ValueError("Phone number must be at least 8 digits long")

        return cleaned_number


class GetCode(BaseModel):
    query_id: str
    telephone: str
    code: int


class User(BaseModel):
    id: int
    telephone: str | None
    email: EmailStr | None

    cloud_primary_key: str | None
    cloud_secondary_key: str | None
    cloud_third_key: str | None

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
            raise ValueError("Phone number must be at least 10 digits long")

        return cleaned_number

    @field_validator("email")
    def validate_email(cls, value: str | None) -> str | None:
        if not value:
            return None

        return value.lower()

    @field_validator("cloud_primary_key", "cloud_secondary_key", "cloud_third_key")
    def validate_cloud_primary_key(cls, value: str | None) -> str | None:
        if not value:
            return None

        if len(value) < 3:
            raise ValueError("Cloud key must be at least 3 characters long")

        return value
