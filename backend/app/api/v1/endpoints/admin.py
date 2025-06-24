from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models import get_db
from app.models.request import Request, RequestStatus
from app.models.user import User, UserRole
from app.core.security import get_current_user

router = APIRouter()
security = HTTPBearer()


class UpdateRequestStatus(BaseModel):
    status: RequestStatus


def get_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    user = get_current_user(db, credentials.credentials)
    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.patch("/requests/{request_id}/status")
async def update_request_status(
    request_id: int,
    status_data: UpdateRequestStatus,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    request.status = status_data.status
    db.commit()
    db.refresh(request)
    return request
