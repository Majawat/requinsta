from dataclasses import asdict
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models import get_db
from app.models.setting import Setting
from app.models.media_manager import MediaManagerInstance
from app.models.user import User
from app.api.v1.deps import get_admin_user
from app.plugins.descriptor import (
    METADATA_PROVIDER,
    NOTIFIER,
    CONFIG_GLOBAL,
    CONFIG_INSTANCE,
    CONFIG_NONE,
)
from app.plugins.discovery import discover

router = APIRouter()

# Plugin types whose config lives globally (settings table) and that this
# generic config API can save. Instance-scoped types (media managers) keep their
# dedicated endpoints because they have many instances + dynamic options.
_TESTABLE = {METADATA_PROVIDER, NOTIFIER}


def _find(plugin_type: str, key: str):
    for d in discover():
        if d.plugin_type == plugin_type and d.key == key:
            return d
    raise HTTPException(status_code=404, detail="Plugin not found")


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


class ConfigFieldValue(BaseModel):
    key: str
    label: str
    type: str
    required: bool
    secret: bool
    help: Optional[str] = None
    default: Any = None
    options: Optional[List[Any]] = None
    value: Any = None       # current value (empty for secrets)
    is_set: bool = False     # whether a value is stored (so secrets can show "set")


class PluginConfigResponse(BaseModel):
    id: str
    display_name: str
    plugin_type: str
    config_scope: str
    testable: bool
    fields: List[ConfigFieldValue]


class PluginConfigUpdate(BaseModel):
    values: Dict[str, Any]


def _config_response(db: Session, descriptor) -> PluginConfigResponse:
    keys = [f.key for f in descriptor.config_schema]
    stored = {
        s.key: s.value
        for s in db.query(Setting).filter(Setting.key.in_(keys)).all()
    } if keys else {}

    fields = []
    for f in descriptor.config_schema:
        is_set = bool(stored.get(f.key))
        fields.append(
            ConfigFieldValue(
                key=f.key,
                label=f.label,
                type=f.type,
                required=f.required,
                secret=f.secret,
                help=f.help,
                default=f.default,
                options=f.options,
                # Never echo a secret value back; non-secrets return the stored value.
                value=("" if f.secret else stored.get(f.key, f.default)),
                is_set=is_set,
            )
        )
    return PluginConfigResponse(
        id=descriptor.id,
        display_name=descriptor.display_name,
        plugin_type=descriptor.plugin_type,
        config_scope=descriptor.config_scope,
        testable=descriptor.plugin_type in _TESTABLE,
        fields=fields,
    )


@router.get("/{plugin_type}/{key}/config", response_model=PluginConfigResponse)
def get_plugin_config(
    plugin_type: str,
    key: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    descriptor = _find(plugin_type, key)
    if descriptor.config_scope != CONFIG_GLOBAL:
        raise HTTPException(
            status_code=400,
            detail="This plugin is not globally configured "
            "(instance-scoped plugins are managed under Media Managers)",
        )
    return _config_response(db, descriptor)


@router.put("/{plugin_type}/{key}/config", response_model=PluginConfigResponse)
def update_plugin_config(
    plugin_type: str,
    key: str,
    body: PluginConfigUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    descriptor = _find(plugin_type, key)
    if descriptor.config_scope != CONFIG_GLOBAL:
        raise HTTPException(status_code=400, detail="Plugin is not globally configured")

    schema_by_key = {f.key: f for f in descriptor.config_schema}
    for field_key, raw in body.values.items():
        field = schema_by_key.get(field_key)
        if field is None:
            continue  # ignore unknown keys
        # A blank secret means "leave the stored value untouched".
        if field.secret and (raw is None or str(raw) == ""):
            continue
        if raw is None:
            continue
        value = "true" if raw is True else "false" if raw is False else str(raw)
        existing = db.query(Setting).filter(Setting.key == field_key).first()
        if existing:
            existing.value = value
        else:
            db.add(Setting(key=field_key, value=value, is_secret=field.secret,
                           description=field.label))
    db.commit()

    # Let providers that cache their key pick up the change without a restart.
    obj = descriptor.obj
    if hasattr(obj, "invalidate_api_key_cache"):
        try:
            obj.invalidate_api_key_cache()
        except Exception:
            pass

    return _config_response(db, descriptor)


@router.post("/{plugin_type}/{key}/test")
async def test_plugin(
    plugin_type: str,
    key: str,
    admin: User = Depends(get_admin_user),
):
    descriptor = _find(plugin_type, key)
    obj = descriptor.obj

    if plugin_type == NOTIFIER:
        if not obj.is_configured():
            raise HTTPException(status_code=400, detail="Notifier is not configured")
        result = await obj.send(
            admin.email,
            "Requinsta test notification",
            "This is a test message from Requinsta. If you received it, it works.",
        )
        return {"ok": result.ok, "message": result.message}

    if plugin_type == METADATA_PROVIDER:
        media_type = (descriptor.media_types or ["book"])[0]
        try:
            results = await obj.search("the lord of the rings", media_type)
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "message": f"Search failed: {e}"}
        n = len(results)
        return {
            "ok": n > 0,
            "message": f"{n} result(s) for a sample search"
            if n
            else "No results (check the API key/token)",
        }

    raise HTTPException(status_code=400, detail="This plugin type has no test action")
