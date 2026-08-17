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
    TIMEOUT = 20.0

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
        # Readarr lookup takes a free-text term; author+title matches what a human
        # would type. (Hardcover ids don't map to Readarr's Goodreads/edition ids,
        # so we search by name rather than by external_id.)
        term = request.title or ""
        if getattr(request, "author", None):
            term = f"{term} {request.author}"
        term = term.strip()
        if not term:
            return None
        resp = await self._get(config, "/book/lookup", term=term)
        if resp.status_code != 200:
            return None
        results = resp.json() or []
        return results[0] if results else None

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

        author = dict(book.get("author") or {})
        author.update(
            {
                "qualityProfileId": config.quality_profile_id,
                "metadataProfileId": config.metadata_profile_id or 1,
                "rootFolderPath": config.root_folder_path,
                "monitored": True,
                "addOptions": {"searchForMissingBooks": False},
            }
        )
        payload = dict(book)
        payload.update(
            {
                "author": author,
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
