# Requinsta plugins (drop-in)

Any `*.py` file placed in this directory is discovered at startup and its plugins
are registered — no core code changes, no rebuild. This directory is mounted into
the backend container at `/plugins` (see `docker-compose.yml`).

A plugin file must expose either:

- `PLUGINS: list[PluginDescriptor]`, or
- `get_plugins() -> list[PluginDescriptor]`

Files whose names start with `_` are skipped (use that for examples/WIP).

## Anatomy

A plugin implements one of the type interfaces from `app.plugins.base`
(`MetadataProvider`, `MediaManager`, `Notifier`, and later `LibraryProvider`) and
describes itself with a `PluginDescriptor` from `app.plugins.descriptor`:

```python
from app.plugins.base import Notifier, NotificationResult
from app.plugins.descriptor import PluginDescriptor, ConfigField, NOTIFIER, CONFIG_GLOBAL

class MyNotifier(Notifier):
    @property
    def service(self): return "mychannel"
    def is_configured(self): return True
    async def send(self, to, subject, body):
        return NotificationResult(ok=True, message="sent")

PLUGINS = [
    PluginDescriptor(
        plugin_type=NOTIFIER,
        key="mychannel",
        display_name="My Channel",
        version="0.1.0",
        obj=MyNotifier(),
        config_scope=CONFIG_GLOBAL,
        config_schema=[ConfigField(key="MYCHANNEL_URL", label="Webhook URL", required=True, secret=True)],
    )
]
```

Built-in plugins use this same contract — a third-party plugin is a first-class
citizen. A third-party plugin cannot shadow a built-in with the same
`(plugin_type, key)`.

## Distribution options

1. **Drop-in** (this directory) — simplest for self-hosting.
2. **pip package** — advertise the `requinsta.plugins` entry point returning the
   same descriptor list.
