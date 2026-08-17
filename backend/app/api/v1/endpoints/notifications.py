from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models.user import User
from app.api.v1.deps import get_admin_user
from app.plugins.notifier_registry import notifier_registry

router = APIRouter()


class NotifierStatus(BaseModel):
    service: str
    configured: bool


class TestRequest(BaseModel):
    # Where to send the test; defaults to the requesting admin's own email.
    to: Optional[str] = None
    service: str = "email"


@router.get("/services", response_model=List[NotifierStatus])
def list_notifiers(_: User = Depends(get_admin_user)):
    return [
        NotifierStatus(service=n.service, configured=n.is_configured())
        for n in notifier_registry.notifiers.values()
    ]


@router.post("/test")
async def send_test(
    body: TestRequest = TestRequest(),
    admin: User = Depends(get_admin_user),
):
    notifier = notifier_registry.get(body.service)
    if not notifier:
        raise HTTPException(status_code=400, detail=f"Unknown notifier '{body.service}'")
    if not notifier.is_configured():
        raise HTTPException(status_code=400, detail=f"{body.service} is not configured")

    to = body.to or admin.email
    result = await notifier.send(
        to,
        "Requinsta test notification",
        "This is a test message from Requinsta. If you received it, notifications work.",
    )
    return result.model_dump()
