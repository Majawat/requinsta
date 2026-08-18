# Requinsta

Universal media request system for self-hosted home media libraries — a
request/approve workflow for **every** media type (books, audiobooks, music,
movies, TV, comics), not just movies/TV.

Users search for a title, request it, and get notified when it's available.
Admins approve requests, which are pushed to downstream managers (Readarr,
Lidarr, …). Everything downstream is a **plugin**.

## Highlights

- **Manager-first search** — search a media type and it queries that type's media
  manager directly (its own catalog). Results are exactly what can be fulfilled,
  with the manager's own ids, so availability and "add" are always in sync. A
  standalone metadata provider can be used instead per type.
- **"Already available" / "already requested"** shown on search results.
- **End-to-end fulfillment** — approve → push to the manager → if already owned
  it's fulfilled instantly, else a background poller auto-fulfills when the
  download completes → the requester is emailed.
- **Issue reporting** on available media, with an admin queue.
- **Discoverable plugin architecture** — metadata providers, media managers, and
  notifiers are plugins; drop a `.py` in `/plugins` or ship a pip package. See
  [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
- **Account self-service**, role-based admin, dark responsive UI.

## Media types & adapters

| Type | Search source | Fulfillment |
|------|---------------|-------------|
| audiobook | Readarr (manager) | ✅ |
| music | Lidarr (manager) | ✅ |
| book | Hardcover / OpenLibrary (provider) | add a Readarr-books instance |
| movie / tv | TMDB (provider) | needs Radarr / Sonarr adapters |
| comic | — | needs a Mylar adapter |

## Quick start

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API + docs: http://localhost:8000/docs

The first registered user becomes **admin**. Configure your media managers under
**Admin → Media Managers**, and (optionally) metadata providers / search source
under **Admin → Plugins**.

## Stack

- **Backend**: FastAPI · SQLAlchemy · PostgreSQL · Alembic (auth via bcrypt +
  PyJWT). Schema is owned by Alembic migrations (run on startup).
- **Frontend**: Vue 3 · Vite · Pinia · Vue Router · Tailwind CSS.
- **Deployment**: Docker Compose (a plugins volume is mounted at `/plugins`).

## Docs

- [Architecture](docs/ARCHITECTURE.md) — plugin system, request lifecycle, adapters.
- [Handover / status](docs/HANDOVER.md) — current state, how to test, what's next.
- [Design brief](docs/DESIGN_BRIEF.md) — UI/UX direction.

## License

MIT — see LICENSE.
