"""Plugin discovery: built-ins + third-party plugins.

Third-party plugins are found two ways:
  1. Directory drop-in: any `*.py` in PLUGINS_DIR exposing `PLUGINS` (a list of
     PluginDescriptor) or `get_plugins()`. Ideal for a mounted volume.
  2. Entry points: a pip-installed package advertising the `requinsta.plugins`
     entry-point group.

Built-ins always load; a third-party plugin with the same (type, key) is ignored
so it cannot silently shadow a shipped plugin.
"""
import glob
import importlib.util
import os
from typing import List

from app.plugins.descriptor import PluginDescriptor
from app.plugins import builtin
from app.core.config import settings

_cache: List[PluginDescriptor] | None = None


def _from_module(module) -> List[PluginDescriptor]:
    plugins = getattr(module, "PLUGINS", None)
    if plugins is None and hasattr(module, "get_plugins"):
        plugins = module.get_plugins()
    return list(plugins) if plugins else []


def _load_directory(path: str) -> List[PluginDescriptor]:
    out: List[PluginDescriptor] = []
    if not path or not os.path.isdir(path):
        return out
    for file in sorted(glob.glob(os.path.join(path, "*.py"))):
        name = os.path.splitext(os.path.basename(file))[0]
        if name.startswith("_"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(f"requinsta_plugin_{name}", file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for d in _from_module(module):
                d.source = "directory"
                out.append(d)
        except Exception as e:  # noqa: BLE001 - a bad plugin must not crash startup
            print(f"Failed to load plugin file {file}: {e}")
    return out


def _load_entry_points() -> List[PluginDescriptor]:
    out: List[PluginDescriptor] = []
    try:
        from importlib.metadata import entry_points

        eps = entry_points()
        group = (
            eps.select(group="requinsta.plugins")
            if hasattr(eps, "select")
            else eps.get("requinsta.plugins", [])
        )
        for ep in group:
            try:
                loaded = ep.load()
                descriptors = loaded() if callable(loaded) else loaded
                for d in list(descriptors):
                    d.source = "entry_point"
                    out.append(d)
            except Exception as e:  # noqa: BLE001
                print(f"Failed to load plugin entry point {ep!r}: {e}")
    except Exception as e:  # noqa: BLE001
        print(f"Entry-point discovery failed: {e}")
    return out


def _do_discover() -> List[PluginDescriptor]:
    descriptors = list(builtin._builtin_descriptors())
    seen = {(d.plugin_type, d.key) for d in descriptors}
    for d in _load_directory(settings.PLUGINS_DIR) + _load_entry_points():
        if (d.plugin_type, d.key) in seen:
            print(f"Ignoring third-party plugin that shadows built-in: {d.id}")
            continue
        seen.add((d.plugin_type, d.key))
        descriptors.append(d)
    return descriptors


def discover(force: bool = False) -> List[PluginDescriptor]:
    """Return all plugin descriptors, memoized so plugin objects are created once."""
    global _cache
    if _cache is None or force:
        _cache = _do_discover()
    return _cache
