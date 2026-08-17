from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.plugins.base import MediaManager
from app.plugins.readarr import ReadarrManager
from app.models.media_manager import MediaManagerInstance


class MediaManagerRegistry:
    """Holds the available media-manager adapters (one per service) and helps
    locate the configured instances that can fulfill a given media type."""

    def __init__(self):
        self.adapters: Dict[str, MediaManager] = {}
        self._register_default_adapters()

    def _register_default_adapters(self):
        self.register_adapter(ReadarrManager())

    def register_adapter(self, adapter: MediaManager):
        self.adapters[adapter.service] = adapter

    def get_adapter(self, service: str) -> Optional[MediaManager]:
        return self.adapters.get(service)

    def available_services(self) -> List[str]:
        return sorted(self.adapters.keys())

    def instances_for_media_type(
        self, db: Session, media_type: str
    ) -> List[MediaManagerInstance]:
        """Enabled instances whose media_types include media_type and whose
        service has a registered adapter. Empty list => no automated fulfillment
        available for this type (caller falls back to the manual workflow)."""
        instances = (
            db.query(MediaManagerInstance)
            .filter(MediaManagerInstance.enabled.is_(True))
            .all()
        )
        return [
            inst
            for inst in instances
            if inst.service in self.adapters
            and media_type in (inst.media_types or [])
        ]


media_manager_registry = MediaManagerRegistry()
