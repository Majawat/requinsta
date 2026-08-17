import logging

from sqlalchemy.orm import Session

from app.models.request import Request
from app.models.user import User
from app.plugins.notifier_registry import notifier_registry

logger = logging.getLogger(__name__)


async def notify_request_fulfilled(db: Session, request: Request) -> None:
    """Notify the requester that their request is available. Best-effort: sends
    through every configured notifier, swallows failures, and marks the request
    as notified so it won't fire again. No-op if nothing is configured."""
    if request.fulfillment_notified:
        return

    user = db.query(User).filter(User.id == request.user_id).first()
    if not user or not user.email:
        return
    if not user.notify_on_available:
        return

    notifiers = notifier_registry.configured()
    if not notifiers:
        return

    subject = f"Available now: {request.title}"
    body = (
        f'Good news! Your request "{request.title}" is now available.\n\n'
        f"Media type: {request.media_type.value}\n"
    )

    sent_any = False
    for notifier in notifiers:
        try:
            result = await notifier.send(user.email, subject, body)
            sent_any = sent_any or result.ok
            if not result.ok:
                logger.warning("Notifier %s failed: %s", notifier.service, result.message)
        except Exception:  # noqa: BLE001 - best-effort
            logger.exception("Notifier %s raised", notifier.service)

    if sent_any:
        request.fulfillment_notified = True
        db.commit()
