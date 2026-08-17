import os
from typing import List, Optional

import httpx

from app.plugins.base import MetadataProvider, MediaMetadata


class HardcoverProvider(MetadataProvider):
    """Book metadata from Hardcover.app (GraphQL, Typesense-backed search).

    Token is loaded from the settings table (key HARDCOVER_API_TOKEN) with an
    env fallback, mirroring the TMDB provider. No token => search returns [] and
    the provider is effectively absent (graceful degradation).
    """

    ENDPOINT = "https://api.hardcover.app/v1/graphql"
    TOKEN_KEY = "HARDCOVER_API_TOKEN"
    TIMEOUT = 15.0

    def __init__(self):
        self._cached_token: Optional[str] = None

    @property
    def name(self) -> str:
        return "Hardcover"

    @property
    def supported_media_types(self) -> List[str]:
        return ["book", "audiobook"]

    # ---- token loading (settings table -> env fallback) --------------------

    def _get_token(self) -> str:
        # Only a non-empty token is cached, so setting the token through the admin
        # UI takes effect on the next search without a restart (an empty result
        # would otherwise be cached forever).
        if self._cached_token:
            return self._cached_token

        from app.models import SessionLocal
        from app.models.setting import Setting

        db = SessionLocal()
        try:
            setting = db.query(Setting).filter(Setting.key == self.TOKEN_KEY).first()
            if setting and setting.value:
                self._cached_token = setting.value
                return self._cached_token
        except Exception as e:
            print(f"Failed to load Hardcover token from DB: {e}")
        finally:
            db.close()

        return os.getenv(self.TOKEN_KEY, "")

    def invalidate_api_key_cache(self):
        self._cached_token = None

    def _headers(self, token: str) -> dict:
        # Accept a token pasted with or without a leading "Bearer ".
        clean = token[len("Bearer "):] if token.lower().startswith("bearer ") else token
        return {"Authorization": f"Bearer {clean}", "Content-Type": "application/json"}

    async def _graphql(self, token: str, query: str, variables: dict) -> Optional[dict]:
        async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
            resp = await client.post(
                self.ENDPOINT,
                headers=self._headers(token),
                json={"query": query, "variables": variables},
            )
        if resp.status_code != 200:
            return None
        payload = resp.json()
        if payload.get("errors"):
            print(f"Hardcover GraphQL errors: {payload['errors']}")
            return None
        return payload.get("data")

    # ---- interface ---------------------------------------------------------

    _SEARCH = """
    query Search($q: String!) {
      search(query: $q, query_type: "Book", per_page: 10, page: 1) {
        results
      }
    }
    """

    async def search(self, query: str, media_type: str) -> List[MediaMetadata]:
        if media_type not in self.supported_media_types:
            return []
        token = self._get_token()
        if not token:
            return []

        data = await self._graphql(token, self._SEARCH, {"q": query})
        if not data:
            return []

        results = (data.get("search") or {}).get("results")
        hits = results.get("hits", []) if isinstance(results, dict) else []

        out: List[MediaMetadata] = []
        for hit in hits:
            doc = hit.get("document", {}) if isinstance(hit, dict) else {}
            if not doc:
                continue
            out.append(
                MediaMetadata(
                    title=doc.get("title") or "",
                    author=self._authors(doc),
                    year=self._int(doc.get("release_year")),
                    external_id=str(doc.get("id")) if doc.get("id") is not None else None,
                    cover_url=self._cover(doc),
                    description=doc.get("description"),
                )
            )
        return out

    _BY_ID = """
    query BookById($id: Int!) {
      books(where: {id: {_eq: $id}}, limit: 1) {
        id
        title
        release_year
        description
        image { url }
        contributions { author { name } }
      }
    }
    """

    async def get_by_id(self, external_id: str) -> Optional[MediaMetadata]:
        token = self._get_token()
        if not token:
            return None
        try:
            book_id = int(external_id)
        except (TypeError, ValueError):
            return None

        data = await self._graphql(token, self._BY_ID, {"id": book_id})
        if not data:
            return None
        books = data.get("books") or []
        if not books:
            return None
        book = books[0]

        authors = [
            c.get("author", {}).get("name")
            for c in (book.get("contributions") or [])
            if c.get("author")
        ]
        image = book.get("image") or {}
        return MediaMetadata(
            title=book.get("title") or "",
            author=", ".join([a for a in authors if a]) or None,
            year=self._int(book.get("release_year")),
            description=book.get("description"),
            external_id=str(book.get("id")),
            cover_url=image.get("url") if isinstance(image, dict) else None,
        )

    # ---- parsing helpers ---------------------------------------------------

    @staticmethod
    def _authors(doc: dict) -> Optional[str]:
        names = doc.get("author_names")
        if isinstance(names, list) and names:
            return ", ".join(str(n) for n in names if n)
        if isinstance(names, str):
            return names
        return None

    @staticmethod
    def _cover(doc: dict) -> Optional[str]:
        image = doc.get("image")
        if isinstance(image, dict):
            return image.get("url")
        if isinstance(image, str):
            return image
        return doc.get("image_url")

    @staticmethod
    def _int(value) -> Optional[int]:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
