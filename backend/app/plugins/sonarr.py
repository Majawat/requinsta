from typing import Any, Dict, List, Optional

import httpx

from app.plugins.base import MediaManager, FulfillmentResult


class SonarrManager(MediaManager):
    """Adapter for Sonarr (TV), targeting the Sonarr v3 API.

    Series-centric: Sonarr keys on ``tvdbId``. Because the TMDB provider returns
    tmdb ids (a different id space), TV works best manager-first — search hits
    Sonarr's own ``/series/lookup`` so results carry the tvdbId that add and
    availability also use. A whole show is the unit, so every season is monitored
    on add (``monitor_scope`` doesn't apply the way it does to Readarr/Lidarr).
    """

    API = "/api/v3"
    TIMEOUT = 60.0

    @property
    def service(self) -> str:
        return "sonarr"

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

    @staticmethod
    def _has_files(series: Dict) -> bool:
        stats = series.get("statistics") or {}
        return (stats.get("episodeFileCount") or 0) > 0

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
        return FulfillmentResult(ok=True, message=f"Connected (Sonarr {version})")

    async def list_quality_profiles(self, config: Any) -> List[Dict]:
        resp = await self._get(config, "/qualityprofile")
        return resp.json() if resp.status_code == 200 else []

    async def list_metadata_profiles(self, config: Any) -> List[Dict]:
        # Sonarr has no metadata profiles.
        return []

    async def list_root_folders(self, config: Any) -> List[Dict]:
        resp = await self._get(config, "/rootfolder")
        return resp.json() if resp.status_code == 200 else []

    async def _lookup(self, config: Any, request: Any) -> Optional[Dict]:
        # Prefer an exact tvdb match when the request carries a tvdb id, so a noisy
        # title search can't pick the wrong show.
        ext = str(getattr(request, "external_id", "") or "")
        term = f"tvdb:{ext}" if ext else (request.title or "").strip()
        if not term:
            return None
        resp = await self._get(config, "/series/lookup", term=term)
        if resp.status_code != 200:
            return None
        results = resp.json() or []
        if not results:
            return None
        if ext:
            for s in results:
                if str(s.get("tvdbId")) == ext:
                    return s
        return results[0]

    async def _find_in_library(self, config: Any, tvdb_id: Any) -> Optional[Dict]:
        if not tvdb_id:
            return None
        resp = await self._get(config, "/series")
        if resp.status_code != 200:
            return None
        tid = str(tvdb_id)
        for s in resp.json() or []:
            if str(s.get("tvdbId")) == tid:
                return s
        return None

    async def add(self, config: Any, request: Any) -> FulfillmentResult:
        if config.root_folder_path is None or config.quality_profile_id is None:
            return FulfillmentResult(
                ok=False, message="Instance is missing root folder or quality profile"
            )

        try:
            series = await self._lookup(config, request)
        except httpx.HTTPError as e:
            return FulfillmentResult(ok=False, message=f"Lookup failed: {e}")
        if not series:
            return FulfillmentResult(ok=False, message=f"No Sonarr match for '{request.title}'")

        existing = await self._find_in_library(config, series.get("tvdbId"))
        if existing:
            available = self._has_files(existing)
            return FulfillmentResult(
                ok=True,
                external_ref=str(existing.get("id")),
                status="available" if available else "queued",
                message="Already in the library"
                + (" — has episodes" if available else " — monitored, nothing downloaded yet"),
            )

        payload = dict(series)
        payload.update(
            {
                "qualityProfileId": config.quality_profile_id,
                "rootFolderPath": config.root_folder_path,
                "monitored": True,
                "seasonFolder": True,
                # A show is the unit: monitor every season and search for missing eps.
                "addOptions": {"monitor": "all", "searchForMissingEpisodes": True},
            }
        )

        try:
            resp = await self._post(config, "/series", json=payload)
        except httpx.HTTPError as e:
            return FulfillmentResult(ok=False, message=f"Add failed: {e}")

        if resp.status_code in (200, 201):
            created = resp.json() or {}
            ref = created.get("id") or series.get("tvdbId")
            return FulfillmentResult(
                ok=True,
                external_ref=str(ref) if ref is not None else None,
                status="queued",
                message=f"Added '{series.get('title', request.title)}' to Sonarr",
            )
        if resp.status_code == 400 and "already been added" in resp.text.lower():
            return FulfillmentResult(ok=True, status="queued", message="Already in Sonarr")
        return FulfillmentResult(
            ok=False, message=f"Add rejected ({resp.status_code}): {resp.text[:200]}"
        )

    async def search(self, config: Any, query: str) -> list:
        try:
            resp = await self._get(config, "/series/lookup", term=query)
        except httpx.HTTPError:
            return []
        if resp.status_code != 200:
            return []
        out = []
        for s in resp.json() or []:
            out.append(
                {
                    "title": s.get("title") or "",
                    "author": s.get("network") or None,
                    "year": s.get("year") or None,
                    "cover_url": self._poster(s.get("images")),
                    "description": s.get("overview") or "",
                    "external_id": str(s.get("tvdbId")) if s.get("tvdbId") else None,
                    "available": self._has_files(s),
                }
            )
        return out

    async def owned_external_ids(self, config: Any) -> set:
        try:
            resp = await self._get(config, "/series")
        except httpx.HTTPError:
            return set()
        if resp.status_code != 200:
            return set()
        owned = set()
        for s in resp.json() or []:
            if self._has_files(s) and s.get("tvdbId") is not None:
                owned.add(str(s.get("tvdbId")))
        return owned

    async def get_status(self, config: Any, external_ref: str) -> FulfillmentResult:
        try:
            resp = await self._get(config, f"/series/{external_ref}")
        except httpx.HTTPError as e:
            return FulfillmentResult(ok=False, message=f"Status check failed: {e}")
        if resp.status_code != 200:
            return FulfillmentResult(ok=False, message=f"Series {external_ref} not found")
        series = resp.json() or {}
        available = self._has_files(series)
        return FulfillmentResult(
            ok=True,
            external_ref=str(external_ref),
            status="available" if available else "queued",
            message="Has episodes" if available else "Monitored, nothing downloaded yet",
        )
