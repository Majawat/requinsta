from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Boolean
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
    PODCAST = "podcast"
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

    # Fulfillment routing (Phase C). Set when an approved request is pushed to a
    # media manager. Soft reference (no FK) so deleting an instance doesn't touch
    # history. All nullable — an unrouted/manual request has none of these.
    target_instance_id = Column(Integer, nullable=True)
    target_service = Column(String, nullable=True)   # e.g. "readarr"
    external_ref = Column(String, nullable=True)      # id of the item in that manager
    fulfillment_detail = Column(String, nullable=True)  # last add/push result message
    # Guards against re-notifying if the status is toggled through FULFILLED again.
    fulfillment_notified = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
