from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr
from app.models import get_db
from app.models.request import Request, RequestStatus
from app.models.user import User, UserRole
from app.core.security import get_current_user, get_password_hash

router = APIRouter()
security = HTTPBearer()


class UpdateRequestStatus(BaseModel):
    status: RequestStatus


class UpdateUserRole(BaseModel):
    role: UserRole


class CreateUser(BaseModel):
    email: EmailStr
    password: str
    role: UserRole


class UserResponse(BaseModel):
    id: int
    email: str
    role: UserRole


def get_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    user = get_current_user(db, credentials.credentials)
    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    db: Session = Depends(get_db), admin_user: User = Depends(get_admin_user)
):
    users = db.query(User).all()
    return users


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: CreateUser,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
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

    db.delete(user)
    db.commit()
    return {"message": "User deleted"}


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role_data: UpdateUserRole,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = role_data.role
    db.commit()
    db.refresh(user)
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
