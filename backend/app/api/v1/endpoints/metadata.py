from fastapi import APIRouter
from typing import Dict, List
from app.plugins.manager import plugin_manager
from app.plugins.base import MediaMetadata

router = APIRouter()


@router.get("/search")
async def search_metadata(
    query: str, media_type: str
) -> Dict[str, List[MediaMetadata]]:
    """Search for metadata across all available providers"""
    return await plugin_manager.search_metadata(query, media_type)
