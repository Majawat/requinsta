from dataclasses import asdict
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models import get_db
from app.models.setting import Setting
from app.models.media_manager import MediaManagerInstance
from app.models.user import User
from app.api.v1.deps import get_admin_user
from app.plugins.descriptor import (
    CONFIG_GLOBAL,
    CONFIG_INSTANCE,
    CONFIG_NONE,
)
from app.plugins.discovery import discover

router = APIRouter()


class PluginInfo(BaseModel):
    id: str
    plugin_type: str
    key: str
    display_name: str
    version: str
    source: str
    config_scope: str
    media_types: List[str] | None = None
    config_schema: list
    configured: bool
    instance_count: int = 0


def _is_configured(db: Session, descriptor) -> tuple[bool, int]:
    """Returns (configured, instance_count). Config-scope specific:
    - none: always ready.
    - global: every required setting key has a value.
    - instance: at least one enabled instance exists for this service."""
    if descriptor.config_scope == CONFIG_NONE:
        return True, 0

    if descriptor.config_scope == CONFIG_INSTANCE:
        count = (
            db.query(MediaManagerInstance)
            .filter(MediaManagerInstance.service == descriptor.key)
            .count()
        )
        enabled = (
            db.query(MediaManagerInstance)
            .filter(
                MediaManagerInstance.service == descriptor.key,
                MediaManagerInstance.enabled.is_(True),
            )
            .count()
        )
        return enabled > 0, count

    # CONFIG_GLOBAL
    required = [f.key for f in descriptor.config_schema if f.required]
    if not required:
        # No required fields but global scope: configured if any schema key is set.
        required = [f.key for f in descriptor.config_schema]
    if not required:
        return True, 0
    rows = {
        s.key: s.value
        for s in db.query(Setting).filter(Setting.key.in_(required)).all()
    }
    return all(rows.get(k) for k in required), 0


@router.get("/", response_model=List[PluginInfo])
def list_plugins(
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    """All discovered plugins (built-in + third-party), their config schema, and
    whether each is configured. Secret values are never included — only the
    schema describing the fields."""
    out: List[PluginInfo] = []
    for d in discover():
        configured, instance_count = _is_configured(db, d)
        out.append(
            PluginInfo(
                id=d.id,
                plugin_type=d.plugin_type,
                key=d.key,
                display_name=d.display_name,
                version=d.version,
                source=d.source,
                config_scope=d.config_scope,
                media_types=d.media_types,
                config_schema=[asdict(f) for f in d.config_schema],
                configured=configured,
                instance_count=instance_count,
            )
        )
    return out
