from sqlalchemy import Column, Integer, String, BigInteger
from .base import Base


class PhoneNumber(Base):
    __tablename__ = "phone_numbers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, unique=True, index=True)
    phone_number = Column(String(20), unique=True)
