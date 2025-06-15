from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from .mapped import user_id
from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[user_id]
    telephone: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(nullable=True, unique=True)

    cloud_primary_key: Mapped[str]
    cload_secondary_key: Mapped[str]
    cload_third_key: Mapped[str]


class UserBL:

    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    def create(self, telephone: str):
        new_user = User(telephone=telephone)
        self.session.add(new_user)
        await self.session.flash()

        return new_user
