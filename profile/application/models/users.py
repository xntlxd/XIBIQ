import json

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from .mapped import user_id, created_at
from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[user_id]

    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    telephone: Mapped[str] = mapped_column(unique=True, nullable=False)
    username: Mapped[str] = mapped_column(nullable=True)

    is_premium: Mapped[bool] = mapped_column(default=False)
    end_premium: Mapped[datetime] = mapped_column(nullable=True)

    avatar: Mapped[str] = mapped_column(nullable=True)

    created_at: Mapped[created_at]

    def get_json(self):
        return json.dumps(
            {
                "id": self.id,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "telephone": self.telephone,
                "username": self.username,
                "is_premium": self.is_premium,
                "end_premium": self.end_premium,
                "created_at": self.created_at,
            }
        )
