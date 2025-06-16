import re
from pydantic import BaseModel, field_validator

class GetQuery(BaseModel):
    query_id: str
    telephone: str
    code: str

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