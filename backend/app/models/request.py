from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.models import Base


class MediaType(str, enum.Enum):
    BOOK = "book"
    AUDIOBOOK = "audiobook"
    MOVIE = "movie"
    TV_SHOW = "tv_show"
    MUSIC = "music"
    COMIC = "comic"
    OTHER = "other"


class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    REVIEWING = "reviewing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    UNAVAILABLE = "unavailable"
    DUPLICATE = "duplicate"


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    media_type = Column(Enum(MediaType), nullable=False)
    status = Column(Enum(RequestStatus), default=RequestStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="requests")
