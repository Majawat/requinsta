from typing import Optional

import httpx

from app.plugins.base import Notifier, NotificationResult

DISCORD_WEBHOOK_URL = "DISCORD_WEBHOOK_URL"


def _setting(key: str) -> Optional[str]:
    from app.models import SessionLocal
    from app.models.setting import Setting

    db = SessionLocal()
    try:
        row = db.query(Setting).filter(Setting.key == key).first()
        return row.value if row else None
    finally:
        db.close()


class DiscordNotifier(Notifier):
    """Posts to a Discord channel via an incoming webhook. Channel-based, so the
    per-user `to` address is ignored — the message goes to the webhook's channel."""

    @property
    def service(self) -> str:
        return "discord"

    def is_configured(self) -> bool:
        return bool(_setting(DISCORD_WEBHOOK_URL))

    async def send(self, to: str, subject: str, body: str) -> NotificationResult:
        url = _setting(DISCORD_WEBHOOK_URL)
        if not url:
            return NotificationResult(ok=False, message="Discord webhook is not configured")
        payload = {
            "embeds": [
                {
                    "title": subject[:256],
                    "description": body[:4000],
                    "color": 0x4F46E5,  # indigo
                    "footer": {"text": "Requinsta"},
                }
            ]
        }
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(url, json=payload)
        except httpx.HTTPError as e:  # best-effort channel
            return NotificationResult(ok=False, message=f"Send failed: {e}")
        if resp.status_code in (200, 204):
            return NotificationResult(ok=True, message="Sent to Discord")
        return NotificationResult(ok=False, message=f"Discord returned {resp.status_code}")
