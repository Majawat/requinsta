from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.models import get_db
from app.models.request import Request, RequestStatus, MediaType
from app.models.user import User, UserRole
from app.api.v1.deps import get_authenticated_user

router = APIRouter()


class RequestCreate(BaseModel):
    title: str
    description: str
    media_type: MediaType


class RequestResponse(BaseModel):
    id: int
    title: str
    description: str
    media_type: MediaType
    status: RequestStatus
    user_id: int


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
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request
