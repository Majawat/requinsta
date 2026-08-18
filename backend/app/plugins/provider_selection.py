"""Admin choice of which metadata provider is active per media type.

Stored in the settings table as ACTIVE_METADATA_PROVIDERS = {media_type: key}.
Aligning the provider with the media manager's metadata source (e.g. Hardcover
for a Hardcover-backed Bookshelf) also makes id-based availability matching exact.
"""
import json
from typing import Optional

from sqlalchemy.orm import Session

from app.models.setting import Setting
from app.plugins.descriptor import METADATA_PROVIDER
from app.plugins.discovery import discover

SETTING_KEY = "ACTIVE_METADATA_PROVIDERS"


def load_map(db: Session) -> dict:
    row = db.query(Setting).filter(Setting.key == SETTING_KEY).first()
    if not row or not row.value:
        return {}
    try:
        m = json.loads(row.value)
        return m if isinstance(m, dict) else {}
    except (ValueError, TypeError):
        return {}


def save_map(db: Session, mapping: dict) -> None:
    row = db.query(Setting).filter(Setting.key == SETTING_KEY).first()
    value = json.dumps(mapping)
    if row:
        row.value = value
    else:
        db.add(
            Setting(
                key=SETTING_KEY,
                value=value,
                description="Active metadata provider per media type",
            )
        )
    db.commit()


def active_provider_names(db: Session, media_type: str) -> Optional[set]:
    """Provider NAMES to restrict search to for this media type, or None for all
    (no selection, or the selected provider is no longer installed)."""
    key = load_map(db).get(media_type)
    if not key:
        return None
    for d in discover():
        if d.plugin_type == METADATA_PROVIDER and d.key == key:
            return {d.obj.name}
    return None


def provider_options() -> dict:
    """{media_type: [{key, name}]} — providers that can serve each media type."""
    options: dict = {}
    for d in discover():
        if d.plugin_type == METADATA_PROVIDER:
            for mt in d.media_types or []:
                options.setdefault(mt, []).append(
                    {"key": d.key, "name": d.display_name}
                )
    return options
