"""Descriptors for the plugins shipped with Requinsta.

These use the identical PluginDescriptor contract that third-party plugins use —
built-ins are just plugins that happen to live in-tree. Instances are created
once here and shared everywhere via discovery.
"""
from app.plugins.descriptor import (
    PluginDescriptor,
    ConfigField,
    METADATA_PROVIDER,
    MEDIA_MANAGER,
    NOTIFIER,
    CONFIG_GLOBAL,
    CONFIG_INSTANCE,
    CONFIG_NONE,
)
from app.plugins.hardcover import HardcoverProvider
from app.plugins.openlibrary import OpenLibraryProvider
from app.plugins.tmdb import TMDBProvider
from app.plugins.readarr import ReadarrManager
from app.plugins.email_notifier import EmailNotifier

_ALL_MEDIA_TYPES = ["book", "audiobook", "movie", "tv_show", "music", "comic", "other"]


def _builtin_descriptors():
    return [
        PluginDescriptor(
            plugin_type=METADATA_PROVIDER,
            key="hardcover",
            display_name="Hardcover",
            version="1.0.0",
            obj=HardcoverProvider(),
            config_scope=CONFIG_GLOBAL,
            media_types=["book", "audiobook"],
            config_schema=[
                ConfigField(
                    key="HARDCOVER_API_TOKEN",
                    label="Hardcover API Token",
                    type="password",
                    required=True,
                    secret=True,
                    help="Hardcover → Account → API",
                )
            ],
        ),
        PluginDescriptor(
            plugin_type=METADATA_PROVIDER,
            key="openlibrary",
            display_name="OpenLibrary",
            version="1.0.0",
            obj=OpenLibraryProvider(),
            config_scope=CONFIG_NONE,
            media_types=["book", "audiobook"],
        ),
        PluginDescriptor(
            plugin_type=METADATA_PROVIDER,
            key="tmdb",
            display_name="TMDB",
            version="1.0.0",
            obj=TMDBProvider(),
            config_scope=CONFIG_GLOBAL,
            media_types=["movie", "tv_show"],
            config_schema=[
                ConfigField(
                    key="TMDB_API_KEY",
                    label="TMDB API Key",
                    type="password",
                    required=True,
                    secret=True,
                    help="themoviedb.org → Settings → API",
                )
            ],
        ),
        PluginDescriptor(
            plugin_type=MEDIA_MANAGER,
            key="readarr",
            display_name="Readarr (and forks)",
            version="1.0.0",
            obj=ReadarrManager(),
            config_scope=CONFIG_INSTANCE,
            media_types=["book", "audiobook"],
            config_schema=[
                ConfigField(key="base_url", label="Base URL", type="string", required=True,
                            help="e.g. http://192.168.1.10:8787"),
                ConfigField(key="api_key", label="API Key", type="password", required=True, secret=True),
                ConfigField(key="media_types", label="Media Types", type="multiselect",
                            options=["book", "audiobook"]),
                ConfigField(key="root_folder_path", label="Root Folder", type="select",
                            help="loaded from the instance"),
                ConfigField(key="quality_profile_id", label="Quality Profile", type="select"),
                ConfigField(key="metadata_profile_id", label="Metadata Profile", type="select"),
            ],
        ),
        PluginDescriptor(
            plugin_type=NOTIFIER,
            key="email",
            display_name="Email (SMTP)",
            version="1.0.0",
            obj=EmailNotifier(),
            config_scope=CONFIG_GLOBAL,
            config_schema=[
                ConfigField(key="SMTP_HOST", label="SMTP Host", type="string", required=True),
                ConfigField(key="SMTP_PORT", label="Port", type="number", default=587),
                ConfigField(key="SMTP_FROM", label="From Address", type="string", required=True),
                ConfigField(key="SMTP_USERNAME", label="Username", type="string"),
                ConfigField(key="SMTP_PASSWORD", label="Password", type="password", secret=True),
                ConfigField(key="SMTP_USE_TLS", label="Use STARTTLS", type="boolean", default=True),
            ],
        ),
    ]
