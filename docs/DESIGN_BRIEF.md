# Design brief: Requinsta — universal self-hosted media request app

> Use this as the prompt/context for a UI/UX design pass.

## What it is
Requinsta is a self-hosted web app where family/friends request media from a home
server, and admins approve it. Think of the *request* half of Overseerr/Jellyseerr,
but for EVERY media type — books, audiobooks, music, movies, TV, comics — not just
movies/TV. Users search for a specific thing, request it, and get notified when
it's available; admins approve requests, which are pushed to downstream managers
(Readarr, Lidarr, etc.).

Design a clean, modern, phone-first UI/UX for it.

## Audience & context
- Primary users: non-technical family/friends on their **phones**, casually
  requesting a specific title. Must be dead-simple and pleasant on mobile.
- Admins: more technical (the homelab owner), often on desktop, doing approvals
  and configuration.
- Self-hosted homelab product; dark theme by default.

## The aesthetic we want (and don't)
This is a **utilitarian request tool**, not a streaming/discovery app. Keep it
clean, calm, and text-forward with covers used as *supporting thumbnails*, not as
the main event.

**Do NOT design:**
- A discovery / "trending" / browse-a-feed experience. There is no discovery
  feature and we don't want one right now.
- A wall of posters / dense cover grid as the primary surface.
- Anything that feels like a media library you scroll for inspiration.

**Do design:**
- A **search-driven** flow: the user knows what they want, types it, requests it.
- Cover thumbnails on individual search results and request cards (a small image
  beside the title/author) — helpful for recognition, never the focus.
- A layout that reads as a tidy list/detail app, closer to an email/task client
  than a streaming service.

## Design goals (priority order)
1. **Mobile-first.** Design the phone layout first; it's the common case.
2. **Responsive to tablet and desktop** — fluid, not a stretched phone view. Use
   extra width for a persistent sidebar, denser lists/tables, and a two-pane
   (list + detail) feel where it helps — without turning into a poster wall.
3. Scannable — clear status at a glance (pill + color), obvious primary action.
4. Fast to the primary action: search → request in as few taps as possible.
5. Accessible: strong contrast, large tap targets, keyboard-friendly on desktop.

## Tech constraints (design within these)
- Vue 3 single-file components + **Tailwind CSS v3** utility classes. Prefer
  standard Tailwind tokens; a small component layer exists (`.card`,
  `.btn-primary`, `.input`, `.badge`).
- Dark theme is the default (gray-900 base, indigo/blue accent today — open to a
  refined palette). Provide exact color tokens.
- No heavy component libraries; implementable with Tailwind + a few inline SVG
  icons.
- Responsive via Tailwind breakpoints (sm 640 / md 768 / lg 1024).

## Screens & states (the full app)

**User-facing**
1. **Auth** — login/register, branded, centered, mobile-friendly.
2. **Home** — search-first: a prominent universal search (media-type selector +
   query) as the hero, plus compact request stats and a short "recent requests"
   strip. No feed, no poster wall.
3. **Search results** — results as a tidy **list** (thumbnail + title +
   author/artist + year + type/source badges). Each result shows one of three
   states: **Available** (already in library — no request button), **Requested**
   (already requested), or a **Request** button. Also a manual "can't find it?"
   request form.
4. **My Requests** — filterable (All / Pending / Approved / Available / Denied)
   list of request rows: thumbnail, title, status pill, and for available items a
   "Report an issue" flow (category + description; shows admin responses inline).
5. **Account** — edit email, change password, notification toggle, request stats.

**Admin** (superset; often desktop, but must work on mobile)
6. **Requests queue** — approve (with a "send to which manager" picker) / deny;
   bulk actions would help.
7. **Issues queue** — open/all/resolved filter; respond + resolve.
8. **Users** — list, roles, create/delete.
9. **Media Managers** — configured Readarr/Lidarr/etc. instances; add/edit with a
   Test-connection action and folder/profile pickers.
10. **Plugins** — installed connectors grouped by type with configured/source
    badges; a schema-driven config form; and a "search source per media type"
    control (default "media manager", or override to a metadata provider).
11. **Settings / Stats** — low-level settings list; simple stat tiles.

**Cross-cutting states to design:** loading (skeletons), empty states (friendly,
with a clear next action), error toasts, success feedback. A **request-detail
view** (thumbnail + metadata + status timeline + comments/issues) as a modal on
desktop / bottom sheet on mobile would tie it together — please design it.

## Navigation
Today: a left sidebar (Dashboard, Browse, My Requests, Admin, Profile) + top bar
(user avatar, sign out); on mobile the sidebar is a hamburger drawer. Propose the
best responsive nav — a **bottom tab bar on mobile** (Home / Search / Requests /
Profile) with the sidebar on desktop is likely better; recommend what you'd do.

## Deliverables
1. A compact **design system**: color tokens (dark, + light if easy), type scale,
   spacing, radius, and the core components (button, card, input, status pill,
   result/request row with thumbnail, nav).
2. **Key screens at mobile AND desktop widths**: Home, Search results, My
   Requests, the request-detail view, and the Admin requests queue.
3. Notes on responsive behavior and the mobile navigation pattern.
4. Any information-architecture changes that make it more intuitive for casual
   mobile users.

Keep it implementable in Vue 3 + Tailwind v3, dark-first, list/detail — not
poster-forward.
