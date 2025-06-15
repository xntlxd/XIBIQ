from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from .mapped import user_id, created_at
from .base import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[user_id]
    telephone: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True)

    cloud_primary_key: Mapped[str]
    cloud_secondary_key: Mapped[str]
    cloud_third_key: Mapped[str]

    created_at: Mapped[created_at]


class UsersBL:
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, telephone: str):
        new_user = Users(telephone=telephone)

        self.session.add(new_user)
        await self.session.flush()

        return new_user
