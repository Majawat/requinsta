from typing import Any, Dict, List, Optional

import httpx

from app.plugins.base import MediaManager, FulfillmentResult


class RadarrManager(MediaManager):
    """Adapter for Radarr (movies), targeting the Radarr v3 API.

    Movie-centric: Radarr keys on ``tmdbId`` (the same id space as the TMDB
    metadata provider), so search results, add, and availability all line up.
    There is no author/artist parent and no metadata profile, so ``monitor_scope``
    doesn't apply — a movie is the unit.
    """

    API = "/api/v3"
    # Cold lookups hit Radarr's metadata backend live and can be slow.
    TIMEOUT = 60.0

    @property
    def service(self) -> str:
        return "radarr"

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

    @staticmethod
    def _poster(images: Any) -> Optional[str]:
        for i in images or []:
            if i.get("coverType") == "poster" and i.get("remoteUrl"):
                return i.get("remoteUrl")
        return next((i.get("remoteUrl") for i in (images or []) if i.get("remoteUrl")), None)

    # ---- interface ---------------------------------------------------------

    async def test_connection(self, config: Any) -> FulfillmentResult:
        try:
            resp = await self._get(config, "/system/status")
        except httpx.HTTPError as e:
            return FulfillmentResult(ok=False, message=f"Unreachable: {e}")
        if resp.status_code == 401:
            return FulfillmentResult(ok=False, message="Invalid API key (401)")
        if resp.status_code != 200:
            return FulfillmentResult(ok=False, message=f"Unexpected status {resp.status_code}")
        version = (resp.json() or {}).get("version", "unknown")
        return FulfillmentResult(ok=True, message=f"Connected (Radarr {version})")

    async def list_quality_profiles(self, config: Any) -> List[Dict]:
        resp = await self._get(config, "/qualityprofile")
        return resp.json() if resp.status_code == 200 else []

    async def list_metadata_profiles(self, config: Any) -> List[Dict]:
        # Radarr has no metadata profiles.
        return []

    async def list_root_folders(self, config: Any) -> List[Dict]:
        resp = await self._get(config, "/rootfolder")
        return resp.json() if resp.status_code == 200 else []

    async def _lookup(self, config: Any, request: Any) -> Optional[Dict]:
        # Prefer an exact tmdb match when the request carries a tmdb id (the TMDB
        # provider's external_id), so a noisy title search can't pick the wrong film.
        ext = str(getattr(request, "external_id", "") or "")
        term = f"tmdb:{ext}" if ext else (request.title or "").strip()
        if not term:
            return None
        resp = await self._get(config, "/movie/lookup", term=term)
        if resp.status_code != 200:
            return None
        results = resp.json() or []
        if not results:
            return None
        if ext:
            for m in results:
                if str(m.get("tmdbId")) == ext:
                    return m
        return results[0]

    async def _find_in_library(self, config: Any, tmdb_id: Any) -> Optional[Dict]:
        if not tmdb_id:
            return None
        resp = await self._get(config, "/movie")
        if resp.status_code != 200:
            return None
        tid = str(tmdb_id)
        for m in resp.json() or []:
            if str(m.get("tmdbId")) == tid:
                return m
        return None

    async def add(self, config: Any, request: Any) -> FulfillmentResult:
        if config.root_folder_path is None or config.quality_profile_id is None:
            return FulfillmentResult(
                ok=False, message="Instance is missing root folder or quality profile"
            )

        try:
            movie = await self._lookup(config, request)
        except httpx.HTTPError as e:
            return FulfillmentResult(ok=False, message=f"Lookup failed: {e}")
        if not movie:
            return FulfillmentResult(ok=False, message=f"No Radarr match for '{request.title}'")

        existing = await self._find_in_library(config, movie.get("tmdbId"))
        if existing:
            available = bool(existing.get("hasFile"))
            return FulfillmentResult(
                ok=True,
                external_ref=str(existing.get("id")),
                status="available" if available else "queued",
                message="Already in the library"
                + (" — available" if available else " — monitored, not yet downloaded"),
            )

        payload = dict(movie)
        payload.update(
            {
                "qualityProfileId": config.quality_profile_id,
                "rootFolderPath": config.root_folder_path,
                "monitored": True,
                "minimumAvailability": "released",
                "addOptions": {"searchForMovie": True},
            }
        )

        try:
            resp = await self._post(config, "/movie", json=payload)
        except httpx.HTTPError as e:
            return FulfillmentResult(ok=False, message=f"Add failed: {e}")

        if resp.status_code in (200, 201):
            created = resp.json() or {}
            ref = created.get("id") or movie.get("tmdbId")
            return FulfillmentResult(
                ok=True,
                external_ref=str(ref) if ref is not None else None,
                status="queued",
                message=f"Added '{movie.get('title', request.title)}' to Radarr",
            )
        if resp.status_code == 400 and "already been added" in resp.text.lower():
            return FulfillmentResult(ok=True, status="queued", message="Already in Radarr")
        return FulfillmentResult(
            ok=False, message=f"Add rejected ({resp.status_code}): {resp.text[:200]}"
        )

    async def search(self, config: Any, query: str) -> list:
        try:
            resp = await self._get(config, "/movie/lookup", term=query)
        except httpx.HTTPError:
            return []
        if resp.status_code != 200:
            return []
        out = []
        for m in resp.json() or []:
            out.append(
                {
                    "title": m.get("title") or "",
                    "author": None,
                    "year": m.get("year") or None,
                    "cover_url": self._poster(m.get("images")),
                    "description": m.get("overview") or "",
                    "external_id": str(m.get("tmdbId")) if m.get("tmdbId") else None,
                    "available": bool(m.get("hasFile")),
                }
            )
        return out

    async def owned_external_ids(self, config: Any) -> set:
        try:
            resp = await self._get(config, "/movie")
        except httpx.HTTPError:
            return set()
        if resp.status_code != 200:
            return set()
        owned = set()
        for m in resp.json() or []:
            if m.get("hasFile") and m.get("tmdbId") is not None:
                owned.add(str(m.get("tmdbId")))
        return owned

    async def get_status(self, config: Any, external_ref: str) -> FulfillmentResult:
        try:
            resp = await self._get(config, f"/movie/{external_ref}")
        except httpx.HTTPError as e:
            return FulfillmentResult(ok=False, message=f"Status check failed: {e}")
        if resp.status_code != 200:
            return FulfillmentResult(ok=False, message=f"Movie {external_ref} not found")
        movie = resp.json() or {}
        available = bool(movie.get("hasFile"))
        return FulfillmentResult(
            ok=True,
            external_ref=str(external_ref),
            status="available" if available else "queued",
            message="Available" if available else "Monitored, not yet downloaded",
        )
