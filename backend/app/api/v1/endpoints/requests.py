from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.models import get_db
from app.models.request import Request, RequestStatus, MediaType
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter()
security = HTTPBearer()


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


def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    user = get_current_user(db, credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


@router.get("/", response_model=List[RequestResponse])
async def get_requests(
    db: Session = Depends(get_db), current_user: User = Depends(get_authenticated_user)
):
    requests = db.query(Request).all()
    return requests


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
