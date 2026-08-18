# Handover / status

_Snapshot for picking the project back up. Updated 2026-08-18._

## Where it stands

A working universal media request system with an end-to-end pipeline for the media
types that have adapters:

- **Audiobook (Readarr) and music (Lidarr): fully manager-first** — search the
  manager's own catalog, "already available" shown on results, approve → push →
  auto-fulfill (instant if owned, else via the poller) → email the requester.
- **Book / movie / TV: search works via metadata providers** (Hardcover /
  OpenLibrary / TMDB); fulfillment needs a Readarr-books instance / Radarr /
  Sonarr adapters.
- **Comic: no source yet** (needs a Mylar3 adapter — different, non-arr API).

Done this far: request CRUD, discoverable plugin architecture (providers /
managers / notifiers, drop-in + entry-point discovery), schema-driven plugin
config, manager-first search + availability, background availability poller,
email notifications, issue reporting, account self-service, role-based admin
(requests / issues / users / media-managers / plugins / settings), a UI polish
pass, and a security cleanup (dropped passlib→bcrypt and jose→PyJWT; `pip-audit`
0). All merged to `main`.

## What's next (suggested order)

1. **UI/UX pass** using `docs/DESIGN_BRIEF.md` (mobile-first, list/detail, not
   poster-forward), then implement the resulting design system + screens. Known
   missing UI pieces: toast system, loading skeletons, request-detail modal/sheet,
   and a mobile bottom-tab nav.
2. **Radarr + Sonarr** adapters (movies/TV) — same arr v1 API as Lidarr, so quick;
   completes movie/TV end-to-end.
3. **Mylar3** adapter (comics) — different API, more work.
4. Nice-to-haves: notify user on issue response; request quotas + auto-approve
   rules; duplicate-request detection (#18); bulk admin actions (#19);
   multi-worker poller safety (currently one poller per worker).

## How to develop / test

- **Docker**: `docker compose up --build`. First registered user is admin.
- **Local dev is on Docker** (the Windows dev box has no Docker/Python); a Linux
  test box **Bastet** (`ssh $BASTET_SSH`, LAN `192.168.9.198`) runs the stack at
  `~/requinsta-test`. Deploy loop: `tar` the tree over SSH (no rsync locally),
  then `docker compose ... on Bastet`. **Do not** `rm -rf ~/requinsta-test` from
  the user account — the backend writes root-owned `__pycache__` into the bind
  mount; extract the tar over the existing dir instead.
- Test URL (LAN): UI http://bastet:3000 (hostname is allow-listed; the raw IP is
  not), API http://192.168.9.198:8000/docs. **Test admin: admin@example.com /
  pw123456.** Pre-v1: wipe the DB freely (`docker compose down -v`).
- The Bastet DB currently has real **Readarr-Audio** (`:8789`) and **Lidarr**
  (`:8686`) instances configured with real API keys, for live pipeline testing.

## Key decisions & gotchas

- **Manager-first search**: the media manager is the metadata source (its
  `/lookup` returns metadata + the exact add id). Keeps ids aligned; providers are
  an optional per-type override. No Hardcover token needed for the common case.
- **JWT subject is the user id** (not email) so changing your email doesn't
  invalidate your token. A token TTL is 30 min.
- **Dependency drift**: several Dependabot majors had landed on `main` without
  their migrations (bcrypt 5, tailwind 4, vite/pinia/vue-router majors). All
  reconciled; tailwind pinned to **v3** (v4 is a breaking config change — a real
  v4 migration is a separate task). Watch new Dependabot majors.
- **Arr forks vary**: Bookshelf (Readarr-hardcover) omits the nested author +
  `editions` from `/book/lookup`; the adapter resolves the author via
  `/author/lookup` and constructs an edition. Cold metadata lookups are slow (60s
  timeout).
- **Bastet has python3; the Windows dev box does not** (parse JSON with grep
  locally, or run parsing on Bastet / in the backend container).

## GitHub

Claude has push + PR + issue access via a fine-grained PAT in
`~/.claude/settings.json` env (`$GITHUB_TOKEN`). Push uses an ephemeral
per-command credential helper (nothing persisted). `gh` is not installed; use the
REST API. Repo default branch `main`.
