from typing import Optional

import httpx

from app.plugins.base import Notifier, NotificationResult

WEBHOOK_URL = "WEBHOOK_URL"


def _setting(key: str) -> Optional[str]:
    from app.models import SessionLocal
    from app.models.setting import Setting

    db = SessionLocal()
    try:
        row = db.query(Setting).filter(Setting.key == key).first()
        return row.value if row else None
    finally:
        db.close()


class WebhookNotifier(Notifier):
    """Generic JSON webhook. POSTs {title, message} to a configured URL — wire it
    into your own automation / any service that accepts a JSON POST."""

    @property
    def service(self) -> str:
        return "webhook"

    def is_configured(self) -> bool:
        return bool(_setting(WEBHOOK_URL))

    async def send(self, to: str, subject: str, body: str) -> NotificationResult:
        url = _setting(WEBHOOK_URL)
        if not url:
            return NotificationResult(ok=False, message="Webhook URL is not configured")
        payload = {"title": subject, "message": body, "source": "requinsta"}
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(url, json=payload)
        except httpx.HTTPError as e:  # best-effort channel
            return NotificationResult(ok=False, message=f"Send failed: {e}")
        if 200 <= resp.status_code < 300:
            return NotificationResult(ok=True, message="Webhook delivered")
        return NotificationResult(ok=False, message=f"Webhook returned {resp.status_code}")
