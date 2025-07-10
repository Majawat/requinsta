from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from app.plugins.manager import plugin_manager
from app.plugins.base import MediaMetadata

router = APIRouter()


class MediaMetadataResponse(BaseModel):
    id: str
    title: str
    description: str
    author: str
    year: int
    genre: str
    cover_url: str
    media_type: str
    provider: str


@router.get("/search")
async def search_metadata(
    query: str, media_type: str
) -> List[MediaMetadataResponse]:
    """Search for metadata across all available providers"""
    provider_results = await plugin_manager.search_metadata(query, media_type)
    
    # Flatten results from all providers
    flattened_results = []
    for provider_name, results in provider_results.items():
        for result in results:
            flattened_results.append(
                MediaMetadataResponse(
                    id=result.external_id or f"{provider_name}_{len(flattened_results)}",
                    title=result.title or "Unknown Title",
                    description=result.description or "No description available",
                    author=result.author or "Unknown Author",
                    year=result.year or 0,
                    genre=result.genre or "Unknown Genre",
                    cover_url=result.cover_url or "",
                    media_type=media_type,
                    provider=provider_name
                )
            )
    
    return flattened_results
