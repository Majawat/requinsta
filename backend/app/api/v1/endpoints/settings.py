from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.models import get_db
from app.models.setting import Setting
from app.models.user import User
from app.api.v1.deps import get_admin_user

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
    value: Optional[str]
    description: Optional[str]
    is_secret: bool

    class Config:
        from_attributes = True


def _mask_setting(setting: Setting) -> SettingResponse:
    return SettingResponse(
        id=setting.id,
        key=setting.key,
        value="***" if setting.is_secret and setting.value else setting.value,
        description=setting.description,
        is_secret=setting.is_secret,
    )


@router.get("/", response_model=List[SettingResponse])
def get_settings(
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    return [_mask_setting(s) for s in db.query(Setting).all()]


@router.post("/", response_model=SettingResponse)
def create_setting(
    setting: SettingCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    existing = db.query(Setting).filter(Setting.key == setting.key).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Setting already exists",
        )

    db_setting = Setting(
        key=setting.key,
        value=setting.value,
        description=setting.description,
        is_secret=setting.is_secret,
    )
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return _mask_setting(db_setting)


@router.put("/{setting_key}", response_model=SettingResponse)
def update_setting(
    setting_key: str,
    setting: SettingUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    db_setting = db.query(Setting).filter(Setting.key == setting_key).first()
    if not db_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found",
        )

    db_setting.value = setting.value
    if setting.description is not None:
        db_setting.description = setting.description

    db.commit()
    db.refresh(db_setting)
    return _mask_setting(db_setting)


@router.delete("/{setting_key}")
def delete_setting(
    setting_key: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    db_setting = db.query(Setting).filter(Setting.key == setting_key).first()
    if not db_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found",
        )

    db.delete(db_setting)
    db.commit()
    return {"message": "Setting deleted successfully"}
