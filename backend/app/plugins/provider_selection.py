"""Which search *source* is active per media type.

A source is either a media manager (search its own catalog via /lookup — the
default, manager-first) or a standalone metadata provider. Stored in settings as
SEARCH_SOURCE = {media_type: "manager" | "provider:<key>"}. Absent => default
(manager if one handles the type, else all providers).

Using the manager as the source keeps search results, add payloads, and
availability in one id space, so there's never a mismatch between what's found
and what can be fulfilled.
"""
import json
from typing import Optional

from sqlalchemy.orm import Session

from app.models.setting import Setting
from app.models.media_manager import MediaManagerInstance
from app.plugins.descriptor import METADATA_PROVIDER
from app.plugins.discovery import discover

SETTING_KEY = "SEARCH_SOURCE"


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
        db.add(Setting(key=SETTING_KEY, value=value, description="Search source per media type"))
    db.commit()


def _media_types_with_manager(db: Session) -> set:
    types: set = set()
    for inst in (
        db.query(MediaManagerInstance).filter(MediaManagerInstance.enabled.is_(True)).all()
    ):
        for mt in inst.media_types or []:
            types.add(mt)
    return types


def source_options(db: Session) -> dict:
    """{media_type: [{id, label}]} — provider overrides per type. The empty
    default (managers first) is added by the UI; these are the alternatives. A
    type with a configured manager is always listed (even with no providers) so
    the admin sees it."""
    options: dict = {mt: [] for mt in _media_types_with_manager(db)}
    for d in discover():
        if d.plugin_type == METADATA_PROVIDER:
            for mt in d.media_types or []:
                options.setdefault(mt, []).append(
                    {"id": f"provider:{d.key}", "label": d.display_name}
                )
    return options


def selected_provider_name(db: Session, media_type: str) -> Optional[str]:
    """If the admin explicitly chose a metadata provider for this type, its
    provider name; otherwise None (meaning: use managers, or fall back to all)."""
    choice = load_map(db).get(media_type, "")
    if not choice.startswith("provider:"):
        return None
    key = choice.split(":", 1)[1]
    for d in discover():
        if d.plugin_type == METADATA_PROVIDER and d.key == key:
            return d.obj.name
    return None
