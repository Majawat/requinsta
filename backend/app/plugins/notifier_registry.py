from typing import Dict, List, Optional

from app.plugins.base import Notifier
from app.plugins.descriptor import NOTIFIER
from app.plugins.discovery import discover


class NotifierRegistry:
    """Holds the available notification channels, discovered from built-ins and
    any third-party plugins."""

    def __init__(self):
        self.notifiers: Dict[str, Notifier] = {}
        for d in discover():
            if d.plugin_type == NOTIFIER:
                self.register(d.obj)

    def register(self, notifier: Notifier):
        self.notifiers[notifier.service] = notifier

    def get(self, service: str) -> Optional[Notifier]:
        return self.notifiers.get(service)

    def configured(self) -> List[Notifier]:
        return [n for n in self.notifiers.values() if n.is_configured()]


notifier_registry = NotifierRegistry()
