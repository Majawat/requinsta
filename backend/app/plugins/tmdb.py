import httpx
import os
from typing import List, Optional, Tuple
from app.plugins.base import MetadataProvider, MediaMetadata


class TMDBProvider(MetadataProvider):

    def __init__(self):
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"
        self._cached_api_key: Optional[str] = None

    def _get_api_key(self) -> str:
        if self._cached_api_key is not None:
            return self._cached_api_key

        from app.models import SessionLocal
        from app.models.setting import Setting

        db = SessionLocal()
        try:
            setting = db.query(Setting).filter(Setting.key == "TMDB_API_KEY").first()
            if setting and setting.value:
                self._cached_api_key = setting.value
                return self._cached_api_key
        except Exception as e:
            print(f"Failed to load TMDB API key from DB: {e}")
        finally:
            db.close()

        self._cached_api_key = os.getenv("TMDB_API_KEY", "")
        return self._cached_api_key

    def invalidate_api_key_cache(self):
        self._cached_api_key = None

    def _extract_title_and_year(self, data: dict) -> Tuple[str, Optional[int]]:
        title = data.get("title") or data.get("name", "")
        year = None
        try:
            if data.get("release_date"):
                year = int(data["release_date"][:4])
            elif data.get("first_air_date"):
                year = int(data["first_air_date"][:4])
        except (ValueError, TypeError):
            pass
        return title, year

    @property
    def name(self) -> str:
        return "TMDB"

    @property
    def supported_media_types(self) -> List[str]:
        return ["movie", "tv_show"]

    async def search(self, query: str, media_type: str) -> List[MediaMetadata]:
        if media_type not in self.supported_media_types:
            return []

        api_key = self._get_api_key()
        if not api_key:
            return []

        endpoint = "movie" if media_type == "movie" else "tv"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/search/{endpoint}",
                params={"api_key": api_key, "query": query},
            )
            if response.status_code != 200:
                return []
            data = response.json()

        results = []
        for item in data.get("results", []):
            title, year = self._extract_title_and_year(item)
            metadata = MediaMetadata(
                title=title,
                description=item.get("overview", ""),
                year=year,
                external_id=str(item.get("id", "")),
                cover_url=self._get_poster_url(item.get("poster_path")),
                genre=", ".join([str(g) for g in item.get("genre_ids", [])]),
            )
            results.append(metadata)

        return results

    async def get_by_id(self, external_id: str) -> Optional[MediaMetadata]:
        import asyncio

        api_key = self._get_api_key()
        if not api_key:
            return None

        async def fetch(media_type: str) -> Optional[dict]:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{media_type}/{external_id}",
                    params={"api_key": api_key},
                )
                return response.json() if response.status_code == 200 else None

        movie_data, tv_data = await asyncio.gather(fetch("movie"), fetch("tv"))
        data = movie_data or tv_data
        if data is None:
            return None

        title, year = self._extract_title_and_year(data)
        return MediaMetadata(
            title=title,
            description=data.get("overview", ""),
            year=year,
            external_id=external_id,
            cover_url=self._get_poster_url(data.get("poster_path")),
            genre=", ".join([g.get("name", "") for g in data.get("genres", [])]),
        )

    def _get_poster_url(self, poster_path: Optional[str]) -> Optional[str]:
        if poster_path:
            return f"{self.image_base_url}{poster_path}"
        return None
