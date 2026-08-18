# Roadmap / backlog

Captured requests not yet implemented. Ordered roughly by priority.

## 1. Media types
`MediaType` enum: `book, audiobook, movie, tv_show, music, comic, podcast, other`.

- **Podcasts** — ✅ DONE (2026-08-18): enum value `PODCAST` (migration 0007) + icon
  + type card. **Manager/metadata mapping deliberately NOT wired yet** — a podcast
  request is a manual request for now; searching the Podcasts type returns nothing +
  the manual-request card. Wire the manager/provider later (Audiobookshelf has no
  arr-style `/lookup`, so likely a metadata-provider + manual-add flow, not
  manager-first).
- **YouTube / web video** — no separate type needed: the user routes these through
  **Sonarr** (their Pinchflat → pf-sonarr bridge), so they ride under tv_show.
- **Manga** — user will consider later (would split from comics; separate manager
  like Komga/Kavita/Suwayomi/Mylar).
- **Magazines / periodicals** — out of scope for now (user decision).

## 2. Per-user media-type access (request ACL)
Admins should restrict which media types a given user can request — e.g. friend A
gets book/audiobook/podcast (Audiobookshelf), friend B gets movie/music/tv (Plex).

Sketch:
- Backend: a per-user `allowed_media_types` (list/JSON column, null/empty = all), or
  a richer per-user → library/manager grant. Enforce on **both** `GET /metadata/search`
  (only search types the user may request) and `POST /requests/` (reject disallowed
  types). Migration + on the user model.
- Frontend: Search type cards + "search everything" filtered to the user's allowed
  types; admin editor in **Setup → Users** to toggle types per user.
- Consider mapping types→libraries so the grant is "Audiobookshelf" / "Plex" rather
  than raw types, which is closer to how the user thinks about it.

## 3. Manager monitor scope (Readarr author/series/book)
**Observed:** requesting one book from an author currently monitors the author's
*whole* catalog. Cause: `ReadarrManager.add()` (backend/app/plugins/readarr.py ~L182)
sends the author with `monitored: True` and no per-book monitor scope, so Readarr
applies its default (monitor all). Same shape will apply to Lidarr (artist vs album).

Plan:
- Per-manager-instance setting `default_monitor`: `single` | `series` | `author`
  (Lidarr: `album` | `artist`). Map to Readarr author `addOptions.monitor`
  (`none`/`specificBook`-style → monitor only the requested book; `all` → author) and
  set sibling books `monitored: false` for the single case.
- Optionally: let the requesting user choose scope at request time (a small control
  on the result row / detail), gated by an admin "allow user to pick" toggle, and
  "request all books for this author/series" as an explicit action.
- Admin UI: expose `default_monitor` in **Setup → Media managers** per instance.

## Also pending (from the design pass)
- Full slate restyle of the remaining admin sub-panels (UserManagement,
  MediaManagers, Plugins, AdminSettings, AdminIssues) — Queue request cards + the
  admin shell are done; these still use the old gray/blue theme.
- `DELETE /requests/{id}` (cancel own pending request) → re-enables the design's
  request "Undo" toast and a "Cancel request" action in the detail sheet.
- Radarr + Sonarr adapters (movies/TV) — same arr v1 as Lidarr.
- Mylar3 adapter (comics) — different API.
- True mobile-viewport QA of the redesign (verified structurally only).
