from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.models import get_db
from app.models.request import Request, RequestStatus, MediaType
from app.models.issue import Issue
from app.models.user import User, UserRole
from app.api.v1.deps import get_authenticated_user, require_media_type_access

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
    require_media_type_access(current_user, request_data.media_type.value)
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


@router.delete("/{request_id}")
async def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    """Delete a request. A user may cancel their own request while it's still
    PENDING (this powers the "undo" on a fresh request and "cancel request" in the
    detail sheet); an admin may delete any request in any status. Deleting a
    request only removes the tracking row — it does not touch the media manager."""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    is_admin = current_user.role == UserRole.ADMIN
    if not is_admin:
        if request.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not your request")
        if request.status != RequestStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail="Only a pending request can be cancelled — ask an admin to remove it.",
            )

    # Remove dependent issues first (issues.request_id has no ON DELETE cascade).
    db.query(Issue).filter(Issue.request_id == request_id).delete(synchronize_session=False)
    db.delete(request)
    db.commit()
    return {"message": "Request deleted"}
