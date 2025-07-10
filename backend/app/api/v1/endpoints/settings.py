from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.models import get_db
from app.models.setting import Setting
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter()


class SettingCreate(BaseModel):
    key: str
    value: str
    description: Optional[str] = None
    is_secret: bool = False


class SettingUpdate(BaseModel):
    value: str
    description: Optional[str] = None


class SettingResponse(BaseModel):
    id: int
    key: str
    value: str
    description: Optional[str]
    is_secret: bool
    
    class Config:
        from_attributes = True


def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/", response_model=List[SettingResponse])
def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all settings (admin only)"""
    settings = db.query(Setting).all()
    
    # Mask secret values
    for setting in settings:
        if setting.is_secret and setting.value:
            setting.value = "***"
    
    return settings


@router.post("/", response_model=SettingResponse)
def create_setting(
    setting: SettingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new setting (admin only)"""
    # Check if setting already exists
    existing = db.query(Setting).filter(Setting.key == setting.key).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Setting already exists"
        )
    
    db_setting = Setting(
        key=setting.key,
        value=setting.value,
        description=setting.description,
        is_secret=setting.is_secret
    )
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    
    # Mask secret value in response
    if db_setting.is_secret:
        db_setting.value = "***"
    
    return db_setting


@router.put("/{setting_key}", response_model=SettingResponse)
def update_setting(
    setting_key: str,
    setting: SettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a setting (admin only)"""
    db_setting = db.query(Setting).filter(Setting.key == setting_key).first()
    if not db_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found"
        )
    
    db_setting.value = setting.value
    if setting.description is not None:
        db_setting.description = setting.description
    
    db.commit()
    db.refresh(db_setting)
    
    # Mask secret value in response
    if db_setting.is_secret:
        db_setting.value = "***"
    
    return db_setting


@router.delete("/{setting_key}")
def delete_setting(
    setting_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a setting (admin only)"""
    db_setting = db.query(Setting).filter(Setting.key == setting_key).first()
    if not db_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found"
        )
    
    db.delete(db_setting)
    db.commit()
    
    return {"message": "Setting deleted successfully"}