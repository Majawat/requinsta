from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.models import get_db
from app.models.request import Request, RequestStatus, MediaType
from app.models.user import User, UserRole
from app.api.v1.deps import get_authenticated_user

router = APIRouter()


class RequestCreate(BaseModel):
    title: str
    description: Optional[str] = None
    media_type: MediaType
    # Optional structured metadata carried from a provider search result.
    # Omitted entirely for a manual request.
    external_id: Optional[str] = None
    provider: Optional[str] = None
    cover_url: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None


class RequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    media_type: MediaType
    status: RequestStatus
    user_id: int
    external_id: Optional[str] = None
    provider: Optional[str] = None
    cover_url: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    target_instance_id: Optional[int] = None
    target_service: Optional[str] = None
    external_ref: Optional[str] = None
    fulfillment_detail: Optional[str] = None
    fulfillment_notified: bool = False
    created_at: Optional[datetime] = None


@router.get("/", response_model=List[RequestResponse])
async def get_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    if current_user.role == UserRole.ADMIN:
        return db.query(Request).all()
    return db.query(Request).filter(Request.user_id == current_user.id).all()


@router.post("/", response_model=RequestResponse)
async def create_request(
    request_data: RequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    request = Request(
        user_id=current_user.id,
        title=request_data.title,
        description=request_data.description,
        media_type=request_data.media_type,
        external_id=request_data.external_id,
        provider=request_data.provider,
        cover_url=request_data.cover_url,
        author=request_data.author,
        year=request_data.year,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request
