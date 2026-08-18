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
**item vs collection: ✅ DONE** (migration 0008, PR #78). Per-instance
`monitor_scope` = `item` (only the requested book/album, new default) | `collection`
(whole author/artist), mapped to arr author/artist `addOptions.monitor` (`none`/`all`)
in Readarr/Lidarr `add()`. Configurable in Setup → Media managers.

**Still pending:**
- **Series-level scope** (a third option between item and author): Readarr's add API
  doesn't expose per-series monitoring cleanly — would need a post-add step (look up
  the added book's series, monitor its other books). Not wired.
- **User-selectable scope** at request time (gated by an admin "allow user to pick"
  toggle), and an explicit "request all books for this author/series" action.

## Also pending (from the design pass)
- Full slate restyle of the remaining admin sub-panels (UserManagement,
  MediaManagers, Plugins, AdminSettings, AdminIssues) — Queue request cards + the
  admin shell are done; these still use the old gray/blue theme.
- `DELETE /requests/{id}` (cancel own pending request) → re-enables the design's
  request "Undo" toast and a "Cancel request" action in the detail sheet.
- Radarr + Sonarr adapters (movies/TV) — same arr v1 as Lidarr.
- Mylar3 adapter (comics) — different API.
- True mobile-viewport QA of the redesign (verified structurally only).
