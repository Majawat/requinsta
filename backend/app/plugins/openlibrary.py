import httpx
from typing import List, Optional
from app.plugins.base import MetadataProvider, MediaMetadata


class OpenLibraryProvider(MetadataProvider):

    @property
    def name(self) -> str:
        return "OpenLibrary"

    @property
    def supported_media_types(self) -> List[str]:
        return ["book", "audiobook"]

    async def search(self, query: str, media_type: str) -> List[MediaMetadata]:
        if media_type not in self.supported_media_types:
            return []

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://openlibrary.org/search.json", params={"q": query, "limit": 10}
            )
            data = response.json()

        results = []
        for doc in data.get("docs", []):
            metadata = MediaMetadata(
                title=doc.get("title", ""),
                author=", ".join(doc.get("author_name", [])),
                year=doc.get("first_publish_year"),
                external_id=doc.get("key", "").replace("/works/", ""),
                cover_url=self._get_cover_url(doc.get("cover_i")),
            )
            results.append(metadata)

        return results

    async def get_by_id(self, external_id: str) -> Optional[MediaMetadata]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://openlibrary.org/works/{external_id}.json"
            )
            if response.status_code != 200:
                return None

            data = response.json()

        return MediaMetadata(
            title=data.get("title", ""),
            description=self._extract_description(data.get("description")),
            external_id=external_id,
            genre=", ".join([s.get("name", "") for s in data.get("subjects", [])[:3]]),
        )

    def _get_cover_url(self, cover_id: Optional[int]) -> Optional[str]:
        if cover_id:
            return f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
        return None

    def _extract_description(self, desc) -> Optional[str]:
        if isinstance(desc, dict):
            return desc.get("value", "")
        return desc if isinstance(desc, str) else None
