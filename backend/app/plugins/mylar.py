from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.plugins.base import MediaManager, FulfillmentResult


class MylarManager(MediaManager):
    """Adapter for Mylar3 (comics).

    Mylar is not an *arr: its API is a single ``/api`` endpoint driven by an
    ``apikey`` + ``cmd`` query string, and there is no root-folder / quality /
    metadata-profile model (Mylar uses its own configured comic location). The id
    space is the ComicVine ``comicid``, consistent across findComic / getIndex /
    getComic, so search results, add, and availability all line up.
    """

    TIMEOUT = 60.0

    @property
    def service(self) -> str:
        return "mylar"

    # ---- low-level helpers -------------------------------------------------

    def _base(self, config: Any) -> str:
        return str(config.base_url).rstrip("/")

    async def _get(self, config: Any, cmd: str, **extra) -> httpx.Response:
        params = {"apikey": config.api_key or "", "cmd": cmd, **extra}
        async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
            return await client.get(f"{self._base(config)}/api", params=params)

    @staticmethod
    def _payload(resp: httpx.Response) -> Tuple[bool, Any]:
        """Mylar wraps some commands in ``{success, data}`` and returns others
        (findComic) as a bare list. Normalise to (ok, data)."""
        try:
            j = resp.json()
        except ValueError:
            return False, None
        if isinstance(j, dict):
            return bool(j.get("success", True)), j.get("data", j)
        return True, j

    @staticmethod
    def _year(value: Any) -> Optional[int]:
        try:
            return int(str(value)[:4])
        except (ValueError, TypeError):
            return None

    # ---- interface ---------------------------------------------------------

    async def test_connection(self, config: Any) -> FulfillmentResult:
        try:
            resp = await self._get(config, "getVersion")
        except httpx.HTTPError as e:
            return FulfillmentResult(ok=False, message=f"Unreachable: {e}")
        if resp.status_code == 401:
            return FulfillmentResult(ok=False, message="Invalid API key (401)")
        if resp.status_code != 200:
            return FulfillmentResult(ok=False, message=f"Unexpected status {resp.status_code}")
        ok, data = self._payload(resp)
        if not ok:
            return FulfillmentResult(ok=False, message="Mylar rejected the API key")
        version = (data or {}).get("current_version", "unknown") if isinstance(data, dict) else "unknown"
        return FulfillmentResult(ok=True, message=f"Connected (Mylar3 {str(version)[:8]})")

    # Mylar has no root folders / profiles; the config UI simply shows nothing to
    # pick, and add() doesn't need them.
    async def list_quality_profiles(self, config: Any) -> List[Dict]:
        return []

    async def list_metadata_profiles(self, config: Any) -> List[Dict]:
        return []

    async def list_root_folders(self, config: Any) -> List[Dict]:
        return []

    async def _find_comic_id(self, config: Any, request: Any) -> Optional[str]:
        """Resolve the ComicVine comicid for a request: use the request's
        external_id when it came from a manager-first search, else look the title
        up and take the first match."""
        ext = str(getattr(request, "external_id", "") or "")
        if ext:
            return ext
        term = (request.title or "").strip()
        if not term:
            return None
        try:
            resp = await self._get(config, "findComic", name=term)
        except httpx.HTTPError:
            return None
        _, data = self._payload(resp)
        if isinstance(data, list) and data:
            cid = data[0].get("comicid")
            return str(cid) if cid is not None else None
        return None

    async def add(self, config: Any, request: Any) -> FulfillmentResult:
        comic_id = await self._find_comic_id(config, request)
        if not comic_id:
            return FulfillmentResult(ok=False, message=f"No Mylar match for '{request.title}'")

        # Already in the library? Don't re-add.
        owned = await self.owned_external_ids(config)
        if comic_id in owned:
            status = await self.get_status(config, comic_id)
            return FulfillmentResult(
                ok=True,
                external_ref=comic_id,
                status=status.status or "queued",
                message="Already in Mylar",
            )

        try:
            resp = await self._get(config, "addComic", id=comic_id)
        except httpx.HTTPError as e:
            return FulfillmentResult(ok=False, message=f"Add failed: {e}")
        ok, _ = self._payload(resp)
        if resp.status_code == 200 and ok:
            return FulfillmentResult(
                ok=True,
                external_ref=comic_id,
                status="queued",
                message=f"Added '{request.title}' to Mylar",
            )
        return FulfillmentResult(
            ok=False, message=f"Add rejected ({resp.status_code}): {resp.text[:200]}"
        )

    async def search(self, config: Any, query: str) -> list:
        try:
            resp = await self._get(config, "findComic", name=query)
        except httpx.HTTPError:
            return []
        _, data = self._payload(resp)
        if not isinstance(data, list):
            return []
        out = []
        for c in data:
            desc = c.get("description")
            if desc in (None, "None"):
                desc = (c.get("deck") or "").strip()
            cid = c.get("comicid")
            out.append(
                {
                    "title": c.get("name") or "",
                    "author": c.get("publisher") or None,
                    "year": self._year(c.get("comicyear")),
                    "cover_url": c.get("comicimage") or c.get("comicthumb"),
                    "description": desc or "",
                    "external_id": str(cid) if cid is not None else None,
                    "available": str(c.get("haveit")).lower() == "yes",
                }
            )
        return out

    async def owned_external_ids(self, config: Any) -> set:
        # getIndex lists the series in Mylar's library. Mylar can't cheaply report
        # per-series file counts in bulk, so "in the library" is the availability
        # signal here (matching findComic's `haveit`).
        try:
            resp = await self._get(config, "getIndex")
        except httpx.HTTPError:
            return set()
        _, data = self._payload(resp)
        if not isinstance(data, list):
            return set()
        return {str(c.get("id")) for c in data if c.get("id") is not None}

    async def get_status(self, config: Any, external_ref: str) -> FulfillmentResult:
        try:
            resp = await self._get(config, "getComic", id=external_ref)
        except httpx.HTTPError as e:
            return FulfillmentResult(ok=False, message=f"Status check failed: {e}")
        ok, data = self._payload(resp)
        if not ok or not isinstance(data, dict):
            return FulfillmentResult(ok=False, message=f"Comic {external_ref} not found")
        issues = data.get("issues") or []
        downloaded = sum(1 for i in issues if str(i.get("status")).lower() == "downloaded")
        available = downloaded > 0
        return FulfillmentResult(
            ok=True,
            external_ref=str(external_ref),
            status="available" if available else "queued",
            message=(f"{downloaded}/{len(issues)} issues downloaded" if issues else "Monitored, nothing downloaded yet"),
        )
