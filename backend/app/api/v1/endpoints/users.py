from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, ConfigDict
from sqlalchemy.orm import Session

from app.models import get_db
from app.models.user import User, UserRole
from app.core.security import get_password_hash, verify_password
from app.api.v1.deps import get_authenticated_user

router = APIRouter()


class MeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: UserRole
    notify_on_available: bool


class UpdateMe(BaseModel):
    email: Optional[EmailStr] = None
    notify_on_available: Optional[bool] = None


class ChangePassword(BaseModel):
    current_password: str
    new_password: str


@router.get("/me", response_model=MeResponse)
def get_me(current_user: User = Depends(get_authenticated_user)):
    return current_user


@router.patch("/me", response_model=MeResponse)
def update_me(
    body: UpdateMe,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    if body.email is not None and body.email != current_user.email:
        taken = (
            db.query(User)
            .filter(User.email == body.email, User.id != current_user.id)
            .first()
        )
        if taken:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = body.email

    if body.notify_on_available is not None:
        current_user.notify_on_available = body.notify_on_available

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/password")
def change_password(
    body: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    if not verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if len(body.new_password) < 8:
        raise HTTPException(
            status_code=400, detail="New password must be at least 8 characters"
        )
    current_user.password_hash = get_password_hash(body.new_password)
    db.commit()
    return {"message": "Password updated"}
