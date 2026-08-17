from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.models import Base


class MediaType(PyEnum):
    BOOK = "book"
    AUDIOBOOK = "audiobook"
    MOVIE = "movie"
    TV_SHOW = "tv_show"
    MUSIC = "music"
    COMIC = "comic"
    OTHER = "other"


class RequestStatus(PyEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    FULFILLED = "FULFILLED"
    DENIED = "DENIED"


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    media_type = Column(Enum(MediaType), nullable=False)
    status = Column(Enum(RequestStatus), default=RequestStatus.PENDING)

    # Structured metadata identity, carried from the metadata provider when the
    # request originates from a search result. All nullable: a purely manual
    # request (no provider) is still valid and relies on title/description alone.
    external_id = Column(String, nullable=True)  # provider-native id, e.g. Hardcover book id
    provider = Column(String, nullable=True)     # provider name, e.g. "Hardcover"
    cover_url = Column(String, nullable=True)
    author = Column(String, nullable=True)
    year = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
