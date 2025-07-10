import httpx
from typing import List, Optional
from app.plugins.base import MetadataProvider, MediaMetadata


class TMDBProvider(MetadataProvider):
    """TMDB provider for movies and TV shows"""
    
    def __init__(self):
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"
    
    def _get_api_key(self):
        """Get API key from database settings or environment variable"""
        from app.models import SessionLocal
        from app.models.setting import Setting
        import os
        
        # First try database settings
        db = SessionLocal()
        try:
            setting = db.query(Setting).filter(Setting.key == "TMDB_API_KEY").first()
            if setting and setting.value:
                return setting.value
        except:
            pass
        finally:
            db.close()
        
        # Fallback to environment variable
        return os.getenv("TMDB_API_KEY", "")

    @property
    def name(self) -> str:
        return "TMDB"

    @property
    def supported_media_types(self) -> List[str]:
        return ["movie", "tv_show"]

    async def search(self, query: str, media_type: str) -> List[MediaMetadata]:
        if media_type not in self.supported_media_types:
            return []
        
        # Get API key dynamically
        api_key = self._get_api_key()
        if not api_key:
            return []

        # Map media_type to TMDB endpoint
        endpoint = "movie" if media_type == "movie" else "tv"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/search/{endpoint}",
                params={"api_key": api_key, "query": query}
            )
            
            if response.status_code != 200:
                return []
                
            data = response.json()

        results = []
        for item in data.get("results", []):
            # Handle different field names between movies and TV shows
            title = item.get("title") or item.get("name", "")
            year = None
            if item.get("release_date"):
                year = int(item.get("release_date").split("-")[0])
            elif item.get("first_air_date"):
                year = int(item.get("first_air_date").split("-")[0])
            
            metadata = MediaMetadata(
                title=title,
                description=item.get("overview", ""),
                year=year,
                external_id=str(item.get("id", "")),
                cover_url=self._get_poster_url(item.get("poster_path")),
                genre=", ".join([str(g) for g in item.get("genre_ids", [])])
            )
            results.append(metadata)

        return results

    async def get_by_id(self, external_id: str) -> Optional[MediaMetadata]:
        # Get API key dynamically
        api_key = self._get_api_key()
        if not api_key:
            return None
            
        # This would need to determine if it's a movie or TV show
        # For now, we'll try movie first, then TV
        for media_type in ["movie", "tv"]:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{media_type}/{external_id}",
                    params={"api_key": api_key}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    title = data.get("title") or data.get("name", "")
                    year = None
                    if data.get("release_date"):
                        year = int(data.get("release_date").split("-")[0])
                    elif data.get("first_air_date"):
                        year = int(data.get("first_air_date").split("-")[0])
                    
                    return MediaMetadata(
                        title=title,
                        description=data.get("overview", ""),
                        year=year,
                        external_id=external_id,
                        cover_url=self._get_poster_url(data.get("poster_path")),
                        genre=", ".join([g.get("name", "") for g in data.get("genres", [])])
                    )
        
        return None

    def _get_poster_url(self, poster_path: Optional[str]) -> Optional[str]:
        if poster_path:
            return f"{self.image_base_url}{poster_path}"
        return None