from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from app.models import Base


class UserRole(PyEnum):
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"
    POWER_USER = "POWER_USER"
    USER = "USER"
    READ_ONLY = "READ_ONLY"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
