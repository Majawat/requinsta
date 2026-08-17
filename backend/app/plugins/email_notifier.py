import asyncio
import smtplib
from email.message import EmailMessage
from typing import Dict, Optional

from app.plugins.base import Notifier, NotificationResult


# Settings-table keys this notifier reads.
SMTP_HOST = "SMTP_HOST"
SMTP_PORT = "SMTP_PORT"
SMTP_USERNAME = "SMTP_USERNAME"
SMTP_PASSWORD = "SMTP_PASSWORD"
SMTP_FROM = "SMTP_FROM"
SMTP_USE_TLS = "SMTP_USE_TLS"


class EmailNotifier(Notifier):
    """SMTP email channel. Config lives in the settings table so it can be set
    through the admin UI; secrets (password) are stored with is_secret=True."""

    @property
    def service(self) -> str:
        return "email"

    def _config(self) -> Dict[str, Optional[str]]:
        from app.models import SessionLocal
        from app.models.setting import Setting

        keys = [SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM, SMTP_USE_TLS]
        db = SessionLocal()
        try:
            rows = db.query(Setting).filter(Setting.key.in_(keys)).all()
            return {r.key: r.value for r in rows}
        finally:
            db.close()

    def is_configured(self) -> bool:
        cfg = self._config()
        return bool(cfg.get(SMTP_HOST) and cfg.get(SMTP_FROM))

    async def send(self, to: str, subject: str, body: str) -> NotificationResult:
        cfg = self._config()
        host = cfg.get(SMTP_HOST)
        sender = cfg.get(SMTP_FROM)
        if not host or not sender:
            return NotificationResult(ok=False, message="Email is not configured")

        try:
            port = int(cfg.get(SMTP_PORT) or 587)
        except (TypeError, ValueError):
            port = 587
        use_tls = str(cfg.get(SMTP_USE_TLS) or "true").lower() in ("1", "true", "yes")
        username = cfg.get(SMTP_USERNAME)
        password = cfg.get(SMTP_PASSWORD)

        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        def _send_blocking():
            # smtplib is blocking; run in a worker thread.
            with smtplib.SMTP(host, port, timeout=15) as server:
                if use_tls:
                    server.starttls()
                if username and password:
                    server.login(username, password)
                server.send_message(msg)

        try:
            await asyncio.to_thread(_send_blocking)
        except Exception as e:  # noqa: BLE001 - best-effort channel
            return NotificationResult(ok=False, message=f"Send failed: {e}")
        return NotificationResult(ok=True, message=f"Sent to {to}")
