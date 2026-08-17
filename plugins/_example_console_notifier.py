"""Example third-party plugin (disabled: filename starts with `_`).

Copy to `console_notifier.py` to enable. Demonstrates the drop-in plugin contract
with a trivial notifier that prints to the backend log instead of sending.
"""
from app.plugins.base import Notifier, NotificationResult
from app.plugins.descriptor import (
    PluginDescriptor,
    NOTIFIER,
    CONFIG_NONE,
)


class ConsoleNotifier(Notifier):
    @property
    def service(self) -> str:
        return "console"

    def is_configured(self) -> bool:
        return True

    async def send(self, to: str, subject: str, body: str) -> NotificationResult:
        print(f"[console-notifier] to={to} subject={subject!r}\n{body}")
        return NotificationResult(ok=True, message=f"logged to console for {to}")


PLUGINS = [
    PluginDescriptor(
        plugin_type=NOTIFIER,
        key="console",
        display_name="Console (example)",
        version="0.1.0",
        obj=ConsoleNotifier(),
        config_scope=CONFIG_NONE,
    )
]
