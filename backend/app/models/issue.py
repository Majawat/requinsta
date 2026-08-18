from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.models import Base


class IssueCategory(PyEnum):
    WRONG_CONTENT = "WRONG_CONTENT"   # wrong edition/version/title
    QUALITY = "QUALITY"               # bad audio/video/scan quality
    PLAYBACK = "PLAYBACK"             # won't open/play
    INCOMPLETE = "INCOMPLETE"         # missing chapters/episodes/pages
    OTHER = "OTHER"


class IssueStatus(PyEnum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


class Issue(Base):
    """A problem a user reports about media they already have (a fulfilled
    request). Optionally answered/closed by an admin."""

    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(Enum(IssueCategory), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(IssueStatus), nullable=False, default=IssueStatus.OPEN)
    admin_response = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
