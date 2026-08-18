from typing import Any, Dict, List, Optional

import httpx

from app.plugins.base import MediaManager, FulfillmentResult


class ReadarrManager(MediaManager):
    """Adapter for Readarr and Readarr-API-compatible forks (Bookshelf, Chaptarr).

    Targets the Readarr v1 API. Adding a book in Readarr is author-centric: we
    look the book up by term, then POST it with the instance's root folder and
    quality/metadata profiles (Readarr creates the author if needed).
    """

    API = "/api/v1"
    # Cold metadata lookups (a new author/book the arr hasn't cached) can be slow
    # because the arr fetches from its metadata backend live.
    TIMEOUT = 60.0

    @property
    def service(self) -> str:
        return "readarr"

    # ---- low-level helpers -------------------------------------------------

    def _base(self, config: Any) -> str:
        return str(config.base_url).rstrip("/")

    def _headers(self, config: Any) -> Dict[str, str]:
        return {"X-Api-Key": config.api_key or ""}

    async def _get(self, config: Any, path: str, **params) -> httpx.Response:
        async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
            return await client.get(
                f"{self._base(config)}{self.API}{path}",
                headers=self._headers(config),
                params=params or None,
            )

    async def _post(self, config: Any, path: str, json: Any) -> httpx.Response:
        async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
            return await client.post(
                f"{self._base(config)}{self.API}{path}",
                headers=self._headers(config),
                json=json,
            )

    # ---- interface ---------------------------------------------------------

    async def test_connection(self, config: Any) -> FulfillmentResult:
        try:
            resp = await self._get(config, "/system/status")
        except httpx.HTTPError as e:
            return FulfillmentResult(ok=False, message=f"Unreachable: {e}")
        if resp.status_code == 401:
            return FulfillmentResult(ok=False, message="Invalid API key (401)")
        if resp.status_code != 200:
            return FulfillmentResult(
                ok=False, message=f"Unexpected status {resp.status_code}"
            )
        version = (resp.json() or {}).get("version", "unknown")
        return FulfillmentResult(ok=True, message=f"Connected (Readarr {version})")

    async def list_quality_profiles(self, config: Any) -> List[Dict]:
        resp = await self._get(config, "/qualityprofile")
        return resp.json() if resp.status_code == 200 else []

    async def list_metadata_profiles(self, config: Any) -> List[Dict]:
        resp = await self._get(config, "/metadataprofile")
        return resp.json() if resp.status_code == 200 else []

    async def list_root_folders(self, config: Any) -> List[Dict]:
        resp = await self._get(config, "/rootfolder")
        return resp.json() if resp.status_code == 200 else []

    async def _lookup(self, config: Any, request: Any) -> Optional[Dict]:
        # Look the book up by term (author + title). When the metadata provider
        # and this Readarr share an id space (e.g. a Hardcover-backed Bookshelf,
        # where foreignBookId == the Hardcover id), prefer an exact id match so a
        # noisy term search can't pick the wrong edition/"summary" book.
        term = (request.title or "").strip()
        if getattr(request, "author", None):
            term = f"{term} {request.author}".strip()
        if not term:
            return None
        resp = await self._get(config, "/book/lookup", term=term)
        if resp.status_code != 200:
            return None
        results = resp.json() or []
        if not results:
            return None

        ext = str(getattr(request, "external_id", "") or "")
        if ext:
            for b in results:
                if str(b.get("foreignBookId")) == ext:
                    return b
        return results[0]

    async def _resolve_author_foreign_id(
        self, config: Any, request: Any, book: Dict
    ) -> Optional[str]:
        # Stock Readarr embeds the author in the book lookup; some forks (Bookshelf)
        # don't, so fall back to an author lookup by name.
        embedded = (book.get("author") or {}).get("foreignAuthorId")
        if embedded:
            return embedded
        name = (getattr(request, "author", None) or book.get("authorTitle") or "").strip()
        if not name:
            return None
        resp = await self._get(config, "/author/lookup", term=name)
        if resp.status_code != 200:
            return None
        authors = resp.json() or []
        return authors[0].get("foreignAuthorId") if authors else None

    async def _find_in_library(
        self, config: Any, foreign_book_id: Any
    ) -> Optional[Dict]:
        """Return the library book with this foreignBookId, if it's already added."""
        if not foreign_book_id:
            return None
        resp = await self._get(config, "/book")
        if resp.status_code != 200:
            return None
        fid = str(foreign_book_id)
        for b in resp.json() or []:
            if str(b.get("foreignBookId")) == fid:
                return b
        return None

    async def add(self, config: Any, request: Any) -> FulfillmentResult:
        if config.root_folder_path is None or config.quality_profile_id is None:
            return FulfillmentResult(
                ok=False,
                message="Instance is missing root folder or quality profile",
            )

        try:
            book = await self._lookup(config, request)
        except httpx.HTTPError as e:
            return FulfillmentResult(ok=False, message=f"Lookup failed: {e}")
        if not book:
            return FulfillmentResult(
                ok=False, message=f"No Readarr match for '{request.title}'"
            )

        # Already in the library? Don't re-add; report whether it's downloaded.
        existing = await self._find_in_library(config, book.get("foreignBookId"))
        if existing:
            stats = existing.get("statistics") or {}
            available = (stats.get("bookFileCount") or 0) > 0
            return FulfillmentResult(
                ok=True,
                external_ref=str(existing.get("id")),
                status="available" if available else "queued",
                message="Already in the library"
                + (" — available" if available else " — monitored, not yet downloaded"),
            )

        try:
            author_fid = await self._resolve_author_foreign_id(config, request, book)
        except httpx.HTTPError as e:
            return FulfillmentResult(ok=False, message=f"Author lookup failed: {e}")
        if not author_fid:
            return FulfillmentResult(
                ok=False, message=f"Could not resolve author for '{request.title}'"
            )

        payload = dict(book)
        # Some Readarr forks omit editions from lookup; Readarr's add needs one.
        if not payload.get("editions") and payload.get("foreignEditionId"):
            payload["editions"] = [
                {
                    "foreignEditionId": payload.get("foreignEditionId"),
                    "title": payload.get("title"),
                    "monitored": True,
                    "manualAdd": True,
                }
            ]
        payload.update(
            {
                "author": {
                    "foreignAuthorId": author_fid,
                    "qualityProfileId": config.quality_profile_id,
                    "metadataProfileId": config.metadata_profile_id or 1,
                    "rootFolderPath": config.root_folder_path,
                    "monitored": True,
                    "addOptions": {"searchForMissingBooks": False},
                },
                "monitored": True,
                "addOptions": {"searchForNewBook": True},
            }
        )

        try:
            resp = await self._post(config, "/book", json=payload)
        except httpx.HTTPError as e:
            return FulfillmentResult(ok=False, message=f"Add failed: {e}")

        if resp.status_code in (200, 201):
            created = resp.json() or {}
            ref = created.get("id") or book.get("foreignBookId")
            return FulfillmentResult(
                ok=True,
                external_ref=str(ref) if ref is not None else None,
                status="queued",
                message=f"Added '{book.get('title', request.title)}' to Readarr",
            )
        if resp.status_code == 400 and "already been added" in resp.text.lower():
            # Idempotent: treat an existing book as success.
            return FulfillmentResult(
                ok=True, status="queued", message="Already in Readarr"
            )
        return FulfillmentResult(
            ok=False, message=f"Add rejected ({resp.status_code}): {resp.text[:200]}"
        )

    @staticmethod
    def _clean_author(author_title: str, title: str) -> str:
        # Readarr's lookup gives an ugly authorTitle like "weir, andy <title>".
        # Strip the title, flip "last, first" -> "First Last".
        a = author_title or ""
        if title and title.lower() in a.lower():
            a = a[: a.lower().rfind(title.lower())].strip()
        if "," in a:
            parts = [p.strip() for p in a.split(",", 1)]
            if len(parts) == 2 and parts[1]:
                a = f"{parts[1]} {parts[0]}"
        return a.strip().title()

    async def search(self, config: Any, query: str) -> list:
        try:
            resp = await self._get(config, "/book/lookup", term=query)
        except httpx.HTTPError:
            return []
        if resp.status_code != 200:
            return []
        out = []
        for b in resp.json() or []:
            title = b.get("title") or ""
            images = b.get("images") or []
            cover = next((i.get("remoteUrl") for i in images if i.get("remoteUrl")), None) \
                or b.get("remoteCover")
            year = None
            rd = b.get("releaseDate")
            if rd:
                try:
                    year = int(str(rd)[:4])
                except (ValueError, TypeError):
                    year = None
            stats = b.get("statistics") or {}
            author = (b.get("author") or {}).get("authorName") \
                or self._clean_author(b.get("authorTitle", ""), title)
            out.append(
                {
                    "title": title,
                    "author": author,
                    "year": year,
                    "cover_url": cover,
                    "description": b.get("overview") or "",
                    "external_id": str(b.get("foreignBookId")) if b.get("foreignBookId") else None,
                    "available": (stats.get("bookFileCount") or 0) > 0,
                }
            )
        return out

    async def owned_external_ids(self, config: Any) -> set:
        try:
            resp = await self._get(config, "/book")
        except httpx.HTTPError:
            return set()
        if resp.status_code != 200:
            return set()
        owned = set()
        for b in resp.json() or []:
            stats = b.get("statistics") or {}
            if (stats.get("bookFileCount") or 0) > 0 and b.get("foreignBookId") is not None:
                owned.add(str(b.get("foreignBookId")))
        return owned

    async def get_status(self, config: Any, external_ref: str) -> FulfillmentResult:
        try:
            resp = await self._get(config, f"/book/{external_ref}")
        except httpx.HTTPError as e:
            return FulfillmentResult(ok=False, message=f"Status check failed: {e}")
        if resp.status_code != 200:
            return FulfillmentResult(
                ok=False, message=f"Book {external_ref} not found"
            )
        book = resp.json() or {}
        stats = book.get("statistics") or {}
        available = (stats.get("bookFileCount") or 0) > 0
        return FulfillmentResult(
            ok=True,
            external_ref=str(external_ref),
            status="available" if available else "queued",
        )
