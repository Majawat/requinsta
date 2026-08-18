from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models import get_db
from app.models.request import Request, RequestStatus, MediaType
from app.models.setting import Setting
from app.models.user import User
from app.api.v1.deps import get_authenticated_user
from app.plugins.manager import plugin_manager
from app.plugins.media_manager_registry import media_manager_registry
from app.plugins.provider_selection import active_provider_names

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
    # "available" (already in a library), "requested" (an active request exists),
    # or None (requestable).
    availability: Optional[str] = None


async def _owned_ids(db: Session, media_type: str) -> set:
    """External ids already available in any configured manager for this type."""
    owned: set = set()
    for inst in media_manager_registry.instances_for_media_type(db, media_type):
        adapter = media_manager_registry.get_adapter(inst.service)
        if adapter is None:
            continue
        try:
            owned |= await adapter.owned_external_ids(inst)
        except Exception:  # noqa: BLE001 - availability is best-effort
            pass
    return owned


@router.get("/search")
async def search_metadata(
    query: str,
    media_type: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_authenticated_user),
) -> List[MediaMetadataResponse]:
    """Search across providers and annotate each result with availability.

    If an admin has chosen an active provider for this media type, only that
    provider is used; otherwise all providers that support the type are queried."""
    allowed = active_provider_names(db, media_type)
    provider_results = await plugin_manager.search_metadata(query, media_type, allowed)

    flattened: List[MediaMetadataResponse] = []
    for provider_name, results in provider_results.items():
        for result in results:
            flattened.append(
                MediaMetadataResponse(
                    id=result.external_id or f"{provider_name}_{len(flattened)}",
                    title=result.title or "Unknown Title",
                    description=result.description or "No description available",
                    author=result.author or "Unknown Author",
                    year=result.year or 0,
                    genre=result.genre or "Unknown Genre",
                    cover_url=result.cover_url or "",
                    media_type=media_type,
                    provider=provider_name,
                )
            )

    # Annotate availability: already in a library, or already requested.
    owned = await _owned_ids(db, media_type)
    try:
        mt = MediaType(media_type)
    except ValueError:
        mt = None
    active_requested = set()
    if mt is not None:
        active_requested = {
            r.external_id
            for r in db.query(Request.external_id)
            .filter(
                Request.external_id.isnot(None),
                Request.media_type == mt,
                Request.status.in_(
                    [RequestStatus.PENDING, RequestStatus.APPROVED, RequestStatus.FULFILLED]
                ),
            )
            .all()
        }
    for item in flattened:
        if item.id in owned:
            item.availability = "available"
        elif item.id in active_requested:
            item.availability = "requested"

    return flattened
