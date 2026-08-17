from typing import Optional

from sqlalchemy.orm import Session

from app.models.request import Request
from app.models.media_manager import MediaManagerInstance
from app.plugins.base import FulfillmentResult
from app.plugins.media_manager_registry import media_manager_registry


def resolve_target_instance(
    db: Session, request: Request, instance_id: Optional[int]
) -> tuple[Optional[MediaManagerInstance], Optional[str]]:
    """Pick the instance to fulfill a request.

    - explicit instance_id: use it (validated: exists, enabled, has adapter,
      handles this media type).
    - no instance_id: auto-select only if exactly one instance is eligible;
      never guess among several.

    Returns (instance, error). Both None means "no eligible instance" (a normal,
    non-error state — the request just stays a manual approval).
    """
    media_type = request.media_type.value
    eligible = media_manager_registry.instances_for_media_type(db, media_type)

    if instance_id is not None:
        chosen = next((i for i in eligible if i.id == instance_id), None)
        if chosen is None:
            return None, "Chosen instance is not eligible for this request"
        return chosen, None

    if len(eligible) == 1:
        return eligible[0], None
    return None, None


async def push_to_manager(
    db: Session, request: Request, instance: MediaManagerInstance
) -> FulfillmentResult:
    """Add a request to a media-manager instance and record the outcome on the
    request. Best-effort: a failed push is recorded, not raised, so approval is
    never blocked by a downstream hiccup."""
    adapter = media_manager_registry.get_adapter(instance.service)
    if adapter is None:
        result = FulfillmentResult(
            ok=False, message=f"No adapter for service '{instance.service}'"
        )
    else:
        result = await adapter.add(instance, request)

    request.target_instance_id = instance.id
    request.target_service = instance.service
    request.fulfillment_detail = result.message
    if result.ok and result.external_ref:
        request.external_ref = result.external_ref
    db.commit()
    db.refresh(request)
    return result
