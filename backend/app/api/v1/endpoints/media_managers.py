from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.models import get_db
from app.models.media_manager import MediaManagerInstance
from app.models.user import User
from app.api.v1.deps import get_admin_user
from app.plugins.media_manager_registry import media_manager_registry

router = APIRouter()


class InstanceCreate(BaseModel):
    service: str
    name: str
    base_url: str
    api_key: Optional[str] = None
    media_types: List[str] = []
    enabled: bool = True
    root_folder_path: Optional[str] = None
    quality_profile_id: Optional[int] = None
    metadata_profile_id: Optional[int] = None


class InstanceUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    media_types: Optional[List[str]] = None
    enabled: Optional[bool] = None
    root_folder_path: Optional[str] = None
    quality_profile_id: Optional[int] = None
    metadata_profile_id: Optional[int] = None


class InstanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service: str
    name: str
    base_url: str
    has_api_key: bool
    media_types: List[str]
    enabled: bool
    root_folder_path: Optional[str] = None
    quality_profile_id: Optional[int] = None
    metadata_profile_id: Optional[int] = None


def _to_response(inst: MediaManagerInstance) -> InstanceResponse:
    return InstanceResponse(
        id=inst.id,
        service=inst.service,
        name=inst.name,
        base_url=inst.base_url,
        has_api_key=bool(inst.api_key),
        media_types=inst.media_types or [],
        enabled=inst.enabled,
        root_folder_path=inst.root_folder_path,
        quality_profile_id=inst.quality_profile_id,
        metadata_profile_id=inst.metadata_profile_id,
    )


def _get_or_404(db: Session, instance_id: int) -> MediaManagerInstance:
    inst = (
        db.query(MediaManagerInstance)
        .filter(MediaManagerInstance.id == instance_id)
        .first()
    )
    if not inst:
        raise HTTPException(status_code=404, detail="Instance not found")
    return inst


@router.get("/services", response_model=List[str])
def list_services(_: User = Depends(get_admin_user)):
    """Media-manager services with a registered adapter (e.g. ["readarr"])."""
    return media_manager_registry.available_services()


@router.get("/", response_model=List[InstanceResponse])
def list_instances(
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    return [_to_response(i) for i in db.query(MediaManagerInstance).all()]


@router.post("/", response_model=InstanceResponse)
def create_instance(
    body: InstanceCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    if not media_manager_registry.get_adapter(body.service):
        raise HTTPException(
            status_code=400, detail=f"Unknown service '{body.service}'"
        )
    inst = MediaManagerInstance(**body.model_dump())
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return _to_response(inst)


@router.put("/{instance_id}", response_model=InstanceResponse)
def update_instance(
    instance_id: int,
    body: InstanceUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    inst = _get_or_404(db, instance_id)
    # Only overwrite fields explicitly provided; a null/omitted api_key keeps the
    # stored key rather than clearing it.
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(inst, field, value)
    db.commit()
    db.refresh(inst)
    return _to_response(inst)


@router.delete("/{instance_id}")
def delete_instance(
    instance_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    inst = _get_or_404(db, instance_id)
    db.delete(inst)
    db.commit()
    return {"message": "Instance deleted"}


@router.post("/{instance_id}/test")
async def test_instance(
    instance_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    inst = _get_or_404(db, instance_id)
    adapter = media_manager_registry.get_adapter(inst.service)
    if not adapter:
        raise HTTPException(status_code=400, detail="No adapter for service")
    result = await adapter.test_connection(inst)
    return result.model_dump()


@router.get("/{instance_id}/options")
async def instance_options(
    instance_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    """Quality/metadata profiles and root folders from the live instance, for
    populating the config dropdowns. Returns {id, name} pairs only."""
    inst = _get_or_404(db, instance_id)
    adapter = media_manager_registry.get_adapter(inst.service)
    if not adapter or not hasattr(adapter, "list_root_folders"):
        raise HTTPException(status_code=400, detail="Adapter has no options")

    quality = await adapter.list_quality_profiles(inst)
    metadata = await adapter.list_metadata_profiles(inst)
    roots = await adapter.list_root_folders(inst)
    return {
        "quality_profiles": [
            {"id": p.get("id"), "name": p.get("name")} for p in quality
        ],
        "metadata_profiles": [
            {"id": p.get("id"), "name": p.get("name")} for p in metadata
        ],
        "root_folders": [
            {"id": r.get("id"), "path": r.get("path")} for r in roots
        ],
    }
