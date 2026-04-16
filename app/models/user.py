from enum import Enum as PyEnum

from sqlalchemy import Boolean, Column, Enum, Integer, String

from app.models.base import Base
from app.models.mixins import TimestampMixin


class UserRole(str, PyEnum):
    admin = "admin"
    user = "user"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.user)
