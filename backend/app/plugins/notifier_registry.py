from typing import Dict, List, Optional

from app.plugins.base import Notifier
from app.plugins.email_notifier import EmailNotifier


class NotifierRegistry:
    """Holds the available notification channels. Email is the first; Discord
    and others can register alongside it later."""

    def __init__(self):
        self.notifiers: Dict[str, Notifier] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register(EmailNotifier())

    def register(self, notifier: Notifier):
        self.notifiers[notifier.service] = notifier

    def get(self, service: str) -> Optional[Notifier]:
        return self.notifiers.get(service)

    def configured(self) -> List[Notifier]:
        return [n for n in self.notifiers.values() if n.is_configured()]


notifier_registry = NotifierRegistry()
