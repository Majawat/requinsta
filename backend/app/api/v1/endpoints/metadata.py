from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models import get_db
from app.models.request import Request, RequestStatus, MediaType
from app.models.user import User
from app.api.v1.deps import get_authenticated_user, require_media_type_access
from app.plugins.manager import plugin_manager
from app.plugins.media_manager_registry import media_manager_registry
from app.plugins.provider_selection import selected_provider_name

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
    owned: set = set()
    for inst in media_manager_registry.instances_for_media_type(db, media_type):
        adapter = media_manager_registry.get_adapter(inst.service)
        if adapter is None:
            continue
        try:
            owned |= await adapter.owned_external_ids(inst)
        except Exception:  # noqa: BLE001
            pass
    return owned


def _mk(item, media_type, provider, availability=None) -> MediaMetadataResponse:
    return MediaMetadataResponse(
        id=item.get("external_id") or f"{provider}_{item.get('title', '')[:20]}",
        title=item.get("title") or "Unknown Title",
        description=item.get("description") or "No description available",
        author=item.get("author") or "Unknown Author",
        year=item.get("year") or 0,
        genre=item.get("genre") or "",
        cover_url=item.get("cover_url") or "",
        media_type=media_type,
        provider=provider,
        availability=availability,
    )


async def _search_via_managers(db: Session, query: str, media_type: str) -> List[MediaMetadataResponse]:
    """Manager-first search: query each configured manager's own catalog. The
    manager's lookup already tells us what it can add and whether it's available."""
    out: List[MediaMetadataResponse] = []
    for inst in media_manager_registry.instances_for_media_type(db, media_type):
        adapter = media_manager_registry.get_adapter(inst.service)
        if adapter is None:
            continue
        try:
            items = await adapter.search(inst, query)
        except Exception:  # noqa: BLE001
            items = []
        # The lookup itself lacks file counts, so determine availability from the
        # library (owned = in library with files).
        try:
            owned = await adapter.owned_external_ids(inst)
        except Exception:  # noqa: BLE001
            owned = set()
        for it in items:
            avail = "available" if it.get("external_id") in owned else None
            out.append(_mk(it, media_type, inst.name, avail))
    return out


async def _search_via_providers(db: Session, query: str, media_type: str, only_name: Optional[str]) -> List[MediaMetadataResponse]:
    allowed = {only_name} if only_name else None
    provider_results = await plugin_manager.search_metadata(query, media_type, allowed)
    out: List[MediaMetadataResponse] = []
    for provider_name, results in provider_results.items():
        for r in results:
            out.append(
                _mk(
                    {
                        "external_id": r.external_id,
                        "title": r.title,
                        "description": r.description,
                        "author": r.author,
                        "year": r.year,
                        "genre": r.genre,
                        "cover_url": r.cover_url,
                    },
                    media_type,
                    provider_name,
                )
            )
    # Providers don't know the library; annotate availability from the manager.
    owned = await _owned_ids(db, media_type)
    for item in out:
        if item.id in owned:
            item.availability = "available"
    return out


@router.get("/search")
async def search_metadata(
    query: str,
    media_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
) -> List[MediaMetadataResponse]:
    """Search the source chosen for this media type. Default is manager-first:
    query the media managers that handle the type (results carry their exact ids
    and availability). If an admin picked a metadata provider, use that instead;
    if nothing handles the type, fall back to all providers."""
    require_media_type_access(current_user, media_type)
    provider_name = selected_provider_name(db, media_type)
    has_managers = bool(media_manager_registry.instances_for_media_type(db, media_type))

    if provider_name:
        results = await _search_via_providers(db, query, media_type, provider_name)
    elif has_managers:
        results = await _search_via_managers(db, query, media_type)
    else:
        results = await _search_via_providers(db, query, media_type, None)

    # Annotate "requested" from existing requests (availability already set above).
    try:
        mt = MediaType(media_type)
    except ValueError:
        mt = None
    if mt is not None:
        requested = {
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
        for item in results:
            if item.availability is None and item.id in requested:
                item.availability = "requested"

    return results
