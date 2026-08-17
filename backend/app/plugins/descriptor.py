"""The public plugin contract.

A plugin is any object implementing one of the type interfaces (MetadataProvider,
MediaManager, Notifier, LibraryProvider) that is exposed to Requinsta through a
PluginDescriptor. Built-in plugins and third-party plugins use the exact same
contract, so an external plugin is a first-class citizen.

Third-party plugins are discovered two ways (see discovery.py):
  1. a `.py` module dropped into the plugins directory (PLUGINS_DIR), or
  2. a pip-installed package advertising the `requinsta.plugins` entry point.
Either must expose a module-level `PLUGINS: list[PluginDescriptor]` (or a
`get_plugins() -> list[PluginDescriptor]`).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional


# Plugin type keys.
METADATA_PROVIDER = "metadata_provider"
MEDIA_MANAGER = "media_manager"
NOTIFIER = "notifier"
LIBRARY = "library"

# Where a plugin's configuration lives.
CONFIG_GLOBAL = "global"      # one config, stored in the settings table
CONFIG_INSTANCE = "instance"  # many instances, stored in a dedicated table
CONFIG_NONE = "none"          # no configuration needed


@dataclass
class ConfigField:
    """One configurable field a plugin needs. The admin UI renders a form from a
    plugin's list of these, so no per-plugin frontend code is required."""

    key: str
    label: str
    type: str = "string"  # string | password | number | boolean | select | multiselect
    required: bool = False
    secret: bool = False
    help: Optional[str] = None
    default: Any = None
    options: Optional[List[Any]] = None  # for select/multiselect


@dataclass
class PluginDescriptor:
    """Everything Requinsta needs to know about a plugin: what it is, how to
    configure it, and the live object that implements its behavior."""

    plugin_type: str
    key: str                       # unique within a plugin_type, e.g. "hardcover"
    display_name: str
    version: str
    obj: Any                       # the MetadataProvider/MediaManager/Notifier/... instance
    source: str = "builtin"        # "builtin" | "directory" | "entry_point"
    config_scope: str = CONFIG_NONE
    config_schema: List[ConfigField] = field(default_factory=list)
    media_types: Optional[List[str]] = None  # for metadata/media/library plugins

    @property
    def id(self) -> str:
        return f"{self.plugin_type}:{self.key}"
