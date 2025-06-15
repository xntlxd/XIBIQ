from datetime import datetime
from .tuned import TunedModel
from pydantic import EmailStr


class ShowUser(TunedModel):
    id: int
    telephone: str
    email: EmailStr | None = None

    cloud_primary_key: str | None = None
    cloud_secondary_key: str | None = None
    cloud_third_key: str | None = None

    created_at: datetime
