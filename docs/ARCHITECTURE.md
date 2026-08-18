# Architecture

## Overview

```
User → search → request → Admin approves → push to media manager
                                              ├─ already owned → FULFILLED now
                                              └─ new → download → poller → FULFILLED
                                                                              → notify
```

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Alembic. Entry `app/main.py`
  (removes `create_all`; Alembic `upgrade head` runs on startup; a background
  fulfillment poller task is started on startup).
- **Frontend**: Vue 3 SFCs, Pinia stores (`auth`, `requests`, `metadata`),
  Vue Router, Tailwind. API base is derived from `window.location.hostname`.

## Plugin system (`app/plugins/`)

Everything downstream is a plugin behind a small contract.

- `descriptor.py` — `PluginDescriptor` + `ConfigField`. A plugin declares its
  `plugin_type` (metadata_provider | media_manager | notifier | library), `key`,
  `version`, `config_scope` (none | global | instance) and a `config_schema` the
  admin UI renders generically.
- `discovery.py` — memoized discovery of: built-ins (`builtin.py`), `*.py`
  drop-ins in `PLUGINS_DIR` (mounted `/plugins`), and `requinsta.plugins` entry
  points. A third-party plugin cannot shadow a built-in `(type, key)`.
- The three registries (`manager.py` metadata, `media_manager_registry.py`,
  `notifier_registry.py`) are populated from discovery.

### Interfaces (`base.py`)
- `MetadataProvider` — `search`, `get_by_id`. (Hardcover, OpenLibrary, TMDB)
- `MediaManager` — `test_connection`, `add`, `get_status`, `owned_external_ids`,
  `search`, plus profile/root-folder lookups. **Stateless**: one adapter shared
  across many configured `MediaManagerInstance` rows; every method takes the
  instance config. (Readarr, Lidarr)
- `Notifier` — `is_configured`, `send`. (Email/SMTP)

### Config scopes
- **global** — stored in the `settings` table (e.g. a provider API key, SMTP).
  Configured via the schema-driven form under Admin → Plugins.
- **instance** — many rows in `media_manager_instances` (e.g. two Readarrs).
  Configured under Admin → Media Managers.
- **none** — no config.

## Search (manager-first)

`GET /metadata/search?query&media_type` (`endpoints/metadata.py`):
1. Resolve the **search source** for the media type
   (`plugins/provider_selection.py`, setting `SEARCH_SOURCE`): default is
   manager-first; an admin can override a type to a specific metadata provider.
2. **Manager path** — query each `MediaManagerInstance` for the type via
   `adapter.search()` (wraps the arr `/lookup`); results carry the manager's
   foreign id as `external_id`. Availability is cross-referenced with
   `owned_external_ids` (in library with files).
3. **Provider path** — query the selected/available metadata providers;
   availability annotated from the managers' `owned_external_ids`.
4. Results annotated `available` / `requested` / (requestable).

Because the search source is the same system that fulfills, ids always align —
no "found something that can't be added" mismatch.

## Request lifecycle

- `models/request.py`: status `PENDING → APPROVED → FULFILLED / DENIED`, plus
  metadata (`external_id`, `provider`, `cover_url`, `author`, `year`) and routing
  (`target_instance_id`, `target_service`, `external_ref`, `fulfillment_detail`,
  `fulfillment_notified`).
- **Approve** (`POST /admin/requests/{id}/approve {instance_id?}`) →
  `services/fulfillment.py`: pick the instance (explicit, or auto if exactly one
  eligible), `adapter.add()`. If the manager reports "available" (already owned),
  mark FULFILLED + notify immediately; otherwise it's queued.
- **Poller** (`services/poller.py`, `FULFILLMENT_POLL_SECONDS`, default 300) — for
  APPROVED requests with an `external_ref`, calls `adapter.get_status`; on
  "available" → FULFILLED + notify.
- **Notify** (`services/notifications.py`) — best-effort via configured notifiers;
  respects `User.notify_on_available`; dedup via `fulfillment_notified`.

## Issues

`models/issue.py` + `endpoints/issues.py`: users report a problem on a FULFILLED
request (category + description); admins list/respond/resolve.

## Adapters (arr family)

`ReadarrManager` (books/audiobooks) and `LidarrManager` (music) target the arr v1
API. Add flow: look up by term (prefer exact match when `external_id` ==
the arr foreign id), resolve the author/artist `foreign*Id`, build the payload
with the instance's root folder + quality/metadata profiles, POST. Handles:
already-in-library detection, missing `editions`/`releases`, and slow cold
metadata lookups (60s timeout). Radarr/Sonarr would follow the same shape;
Mylar3 uses a different API.

## Migrations

`0001` baseline · `0002` media_manager_instances · `0003` request routing ·
`0004` fulfillment_notified · `0005` user notify pref · `0006` issues.
