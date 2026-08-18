"""Background poller: flips approved requests to FULFILLED once the media
manager reports their download is available, and notifies the requester.

This closes the loop for genuinely new items: approve pushes to the manager,
the manager downloads, and this poller detects completion — no admin action
needed. Already-owned items are fulfilled at approve time and never reach here.
"""
import asyncio
import logging

from app.models import SessionLocal
from app.models.request import Request, RequestStatus
from app.models.media_manager import MediaManagerInstance
from app.plugins.media_manager_registry import media_manager_registry
from app.services.notifications import notify_request_fulfilled
from app.core.config import settings

logger = logging.getLogger(__name__)


async def poll_once() -> int:
    """One pass. Returns how many requests were fulfilled."""
    db = SessionLocal()
    fulfilled = 0
    try:
        pending = (
            db.query(Request)
            .filter(
                Request.status == RequestStatus.APPROVED,
                Request.external_ref.isnot(None),
                Request.target_instance_id.isnot(None),
            )
            .all()
        )
        for req in pending:
            inst = (
                db.query(MediaManagerInstance)
                .filter(MediaManagerInstance.id == req.target_instance_id)
                .first()
            )
            if not inst:
                continue
            adapter = media_manager_registry.get_adapter(inst.service)
            if not adapter:
                continue
            try:
                result = await adapter.get_status(inst, req.external_ref)
            except Exception:  # noqa: BLE001 - best-effort
                logger.exception("poll get_status failed for request %s", req.id)
                continue
            if result.ok and result.status == "available":
                req.status = RequestStatus.FULFILLED
                db.commit()
                db.refresh(req)
                await notify_request_fulfilled(db, req)
                fulfilled += 1
        return fulfilled
    finally:
        db.close()


async def poll_loop() -> None:
    interval = settings.FULFILLMENT_POLL_SECONDS
    if interval <= 0:
        logger.info("Fulfillment poller disabled (FULFILLMENT_POLL_SECONDS <= 0)")
        return
    logger.info("Fulfillment poller running every %ss", interval)
    while True:
        try:
            n = await poll_once()
            if n:
                logger.info("Poller fulfilled %d request(s)", n)
        except Exception:  # noqa: BLE001
            logger.exception("Fulfillment poll iteration failed")
        await asyncio.sleep(interval)
