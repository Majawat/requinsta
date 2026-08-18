from typing import Any, Dict, List, Optional

import httpx

from app.plugins.base import MediaManager, FulfillmentResult


class LidarrManager(MediaManager):
    """Adapter for Lidarr (music). Artist-centric like Readarr is author-centric:
    look an album up by term, then POST it with the artist + the instance's root
    folder and quality/metadata profiles."""

    API = "/api/v1"
    TIMEOUT = 60.0

    @property
    def service(self) -> str:
        return "lidarr"

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
            return FulfillmentResult(ok=False, message=f"Unexpected status {resp.status_code}")
        version = (resp.json() or {}).get("version", "unknown")
        return FulfillmentResult(ok=True, message=f"Connected (Lidarr {version})")

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
        # Term is album + artist. When the provider shares Lidarr's id space
        # (MusicBrainz release-group id == foreignAlbumId), prefer an exact match.
        term = (request.title or "").strip()
        if getattr(request, "author", None):
            term = f"{term} {request.author}".strip()
        if not term:
            return None
        resp = await self._get(config, "/album/lookup", term=term)
        if resp.status_code != 200:
            return None
        results = resp.json() or []
        if not results:
            return None
        ext = str(getattr(request, "external_id", "") or "")
        if ext:
            for a in results:
                if str(a.get("foreignAlbumId")) == ext:
                    return a
        return results[0]

    async def _resolve_artist_foreign_id(
        self, config: Any, request: Any, album: Dict
    ) -> Optional[str]:
        embedded = (album.get("artist") or {}).get("foreignArtistId")
        if embedded:
            return embedded
        name = (getattr(request, "author", None) or "").strip()
        if not name:
            return None
        resp = await self._get(config, "/artist/lookup", term=name)
        if resp.status_code != 200:
            return None
        artists = resp.json() or []
        return artists[0].get("foreignArtistId") if artists else None

    async def _find_in_library(self, config: Any, foreign_album_id: Any) -> Optional[Dict]:
        if not foreign_album_id:
            return None
        resp = await self._get(config, "/album")
        if resp.status_code != 200:
            return None
        fid = str(foreign_album_id)
        for a in resp.json() or []:
            if str(a.get("foreignAlbumId")) == fid:
                return a
        return None

    async def search(self, config: Any, query: str) -> list:
        try:
            resp = await self._get(config, "/album/lookup", term=query)
        except httpx.HTTPError:
            return []
        if resp.status_code != 200:
            return []
        out = []
        for a in resp.json() or []:
            images = a.get("images") or []
            cover = next((i.get("remoteUrl") for i in images if i.get("remoteUrl")), None) \
                or a.get("remoteCover")
            year = None
            rd = a.get("releaseDate")
            if rd:
                try:
                    year = int(str(rd)[:4])
                except (ValueError, TypeError):
                    year = None
            artist = (a.get("artist") or {}).get("artistName") or ""
            out.append(
                {
                    "title": a.get("title") or "",
                    "author": artist,
                    "year": year,
                    "cover_url": cover,
                    "description": a.get("overview") or "",
                    "external_id": str(a.get("foreignAlbumId")) if a.get("foreignAlbumId") else None,
                    "available": False,  # availability determined against the library
                }
            )
        return out

    async def owned_external_ids(self, config: Any) -> set:
        try:
            resp = await self._get(config, "/album")
        except httpx.HTTPError:
            return set()
        if resp.status_code != 200:
            return set()
        owned = set()
        for a in resp.json() or []:
            stats = a.get("statistics") or {}
            if (stats.get("trackFileCount") or 0) > 0 and a.get("foreignAlbumId") is not None:
                owned.add(str(a.get("foreignAlbumId")))
        return owned

    async def add(self, config: Any, request: Any) -> FulfillmentResult:
        if config.root_folder_path is None or config.quality_profile_id is None:
            return FulfillmentResult(
                ok=False, message="Instance is missing root folder or quality profile"
            )

        try:
            album = await self._lookup(config, request)
        except httpx.HTTPError as e:
            return FulfillmentResult(ok=False, message=f"Lookup failed: {e}")
        if not album:
            return FulfillmentResult(ok=False, message=f"No Lidarr match for '{request.title}'")

        existing = await self._find_in_library(config, album.get("foreignAlbumId"))
        if existing:
            stats = existing.get("statistics") or {}
            available = (stats.get("trackFileCount") or 0) > 0
            return FulfillmentResult(
                ok=True,
                external_ref=str(existing.get("id")),
                status="available" if available else "queued",
                message="Already in the library"
                + (" — available" if available else " — monitored, not yet downloaded"),
            )

        try:
            artist_fid = await self._resolve_artist_foreign_id(config, request, album)
        except httpx.HTTPError as e:
            return FulfillmentResult(ok=False, message=f"Artist lookup failed: {e}")
        if not artist_fid:
            return FulfillmentResult(
                ok=False, message=f"Could not resolve artist for '{request.title}'"
            )

        # monitor_scope: "collection" monitors the whole artist ("all"); anything
        # else (default "item") monitors only the requested album, added below.
        artist_monitor = (
            "all" if getattr(config, "monitor_scope", "item") == "collection" else "none"
        )
        payload = dict(album)
        payload.update(
            {
                "artist": {
                    "foreignArtistId": artist_fid,
                    "qualityProfileId": config.quality_profile_id,
                    "metadataProfileId": config.metadata_profile_id or 1,
                    "rootFolderPath": config.root_folder_path,
                    "monitored": True,
                    "addOptions": {
                        "searchForMissingAlbums": False,
                        "monitor": artist_monitor,
                    },
                },
                "monitored": True,
                "addOptions": {"searchForNewAlbum": True},
            }
        )

        try:
            resp = await self._post(config, "/album", json=payload)
        except httpx.HTTPError as e:
            return FulfillmentResult(ok=False, message=f"Add failed: {e}")

        if resp.status_code in (200, 201):
            created = resp.json() or {}
            ref = created.get("id") or album.get("foreignAlbumId")
            return FulfillmentResult(
                ok=True,
                external_ref=str(ref) if ref is not None else None,
                status="queued",
                message=f"Added '{album.get('title', request.title)}' to Lidarr",
            )
        if resp.status_code == 400 and "already been added" in resp.text.lower():
            return FulfillmentResult(ok=True, status="queued", message="Already in Lidarr")
        return FulfillmentResult(
            ok=False, message=f"Add rejected ({resp.status_code}): {resp.text[:200]}"
        )

    async def get_status(self, config: Any, external_ref: str) -> FulfillmentResult:
        try:
            resp = await self._get(config, f"/album/{external_ref}")
        except httpx.HTTPError as e:
            return FulfillmentResult(ok=False, message=f"Status check failed: {e}")
        if resp.status_code != 200:
            return FulfillmentResult(ok=False, message=f"Album {external_ref} not found")
        album = resp.json() or {}
        stats = album.get("statistics") or {}
        available = (stats.get("trackFileCount") or 0) > 0
        return FulfillmentResult(
            ok=True,
            external_ref=str(external_ref),
            status="available" if available else "queued",
        )
