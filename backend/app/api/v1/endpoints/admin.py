from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict

from app.models import get_db
from app.models.request import Request, RequestStatus
from app.models.issue import Issue
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.api.v1.deps import get_admin_user, get_staff_user
from app.api.v1.endpoints.requests import RequestResponse
from app.services.fulfillment import resolve_target_instance, push_to_manager
from app.services.notifications import notify_request_fulfilled

router = APIRouter()


class UpdateRequestStatus(BaseModel):
    status: RequestStatus


class ApproveRequest(BaseModel):
    # Which media-manager instance to push to. Omit to auto-select when exactly
    # one instance is eligible, or to approve without pushing when none are.
    instance_id: Optional[int] = None


class UpdateUserRole(BaseModel):
    role: UserRole


class UpdateUserMediaTypes(BaseModel):
    # Empty list / null => unrestricted (all types).
    allowed_media_types: Optional[List[str]] = None


class UpdateUserAutoApprove(BaseModel):
    # Empty list / null => no auto-approval.
    auto_approve_media_types: Optional[List[str]] = None


class CreateUser(BaseModel):
    email: EmailStr
    password: str
    role: UserRole


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: UserRole
    allowed_media_types: Optional[List[str]] = None
    auto_approve_media_types: Optional[List[str]] = None


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    return db.query(User).all()


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: CreateUser,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email, password_hash=hashed_password, role=user_data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    if user_id == admin_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Cascade the user's requests and any issues (no ON DELETE cascade in the
    # schema, so deleting a user with requests would otherwise fail the FK).
    req_ids = [r.id for r in db.query(Request.id).filter(Request.user_id == user_id).all()]
    db.query(Issue).filter(
        (Issue.user_id == user_id) | (Issue.request_id.in_(req_ids))
    ).delete(synchronize_session=False)
    db.query(Request).filter(Request.user_id == user_id).delete(synchronize_session=False)
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role_data: UpdateUserRole,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = role_data.role
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/media-types", response_model=UserResponse)
async def update_user_media_types(
    user_id: int,
    body: UpdateUserMediaTypes,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Normalize an empty selection to NULL (unrestricted) so the two "all types"
    # representations don't diverge.
    user.allowed_media_types = body.allowed_media_types or None
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/auto-approve", response_model=UserResponse)
async def update_user_auto_approve(
    user_id: int,
    body: UpdateUserAutoApprove,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.auto_approve_media_types = body.auto_approve_media_types or None
    db.commit()
    db.refresh(user)
    return user


@router.patch("/requests/{request_id}/status", response_model=RequestResponse)
async def update_request_status(
    request_id: int,
    status_data: UpdateRequestStatus,
    db: Session = Depends(get_db),
    _: User = Depends(get_staff_user),
):
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    request.status = status_data.status
    db.commit()
    db.refresh(request)

    # Notify the requester when their item becomes available.
    if request.status == RequestStatus.FULFILLED:
        await notify_request_fulfilled(db, request)
        db.refresh(request)

    return request


@router.post("/requests/{request_id}/approve", response_model=RequestResponse)
async def approve_request(
    request_id: int,
    body: ApproveRequest = ApproveRequest(),
    db: Session = Depends(get_db),
    _: User = Depends(get_staff_user),
):
    """Approve a request and, if a media-manager instance is eligible/chosen,
    push it there. The push is best-effort: its outcome is recorded on the
    request (fulfillment_detail) but never blocks the approval."""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    instance, error = resolve_target_instance(db, request, body.instance_id)
    if error:
        raise HTTPException(status_code=400, detail=error)

    request.status = RequestStatus.APPROVED
    db.commit()
    db.refresh(request)

    if instance is not None:
        await push_to_manager(db, request, instance)

    return request
