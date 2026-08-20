from typing import Dict, Optional

import httpx

from app.plugins.base import Notifier, NotificationResult

# Full topic URL, e.g. https://ntfy.sh/my-topic or https://ntfy.example.com/alerts
NTFY_URL = "NTFY_URL"
NTFY_TOKEN = "NTFY_TOKEN"  # optional access token for protected topics


def _settings(keys) -> Dict[str, Optional[str]]:
    from app.models import SessionLocal
    from app.models.setting import Setting

    db = SessionLocal()
    try:
        rows = db.query(Setting).filter(Setting.key.in_(keys)).all()
        return {r.key: r.value for r in rows}
    finally:
        db.close()


class NtfyNotifier(Notifier):
    """Pushes to an ntfy topic. The message body is the notification body; the
    subject becomes the ntfy title header."""

    @property
    def service(self) -> str:
        return "ntfy"

    def is_configured(self) -> bool:
        return bool(_settings([NTFY_URL]).get(NTFY_URL))

    async def send(self, to: str, subject: str, body: str) -> NotificationResult:
        cfg = _settings([NTFY_URL, NTFY_TOKEN])
        url = cfg.get(NTFY_URL)
        if not url:
            return NotificationResult(ok=False, message="ntfy URL is not configured")
        headers = {"Title": subject[:250]}
        token = cfg.get(NTFY_TOKEN)
        if token:
            headers["Authorization"] = f"Bearer {token}"
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(url, content=body.encode("utf-8"), headers=headers)
        except httpx.HTTPError as e:  # best-effort channel
            return NotificationResult(ok=False, message=f"Send failed: {e}")
        if 200 <= resp.status_code < 300:
            return NotificationResult(ok=True, message="Pushed to ntfy")
        return NotificationResult(ok=False, message=f"ntfy returned {resp.status_code}")
