from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.models import get_db
from app.models.user import User, UserRole
from app.core.security import get_current_user

security = HTTPBearer()


def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    user = get_current_user(db, credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


def get_admin_user(current_user: User = Depends(get_authenticated_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# Staff can work the queue (approve/deny requests, resolve issues) but only ADMIN
# manages users, media managers, plugins and settings.
STAFF_ROLES = (UserRole.ADMIN, UserRole.MODERATOR)


def is_staff(user: User) -> bool:
    return user.role in STAFF_ROLES


def get_staff_user(current_user: User = Depends(get_authenticated_user)) -> User:
    if not is_staff(current_user):
        raise HTTPException(status_code=403, detail="Moderator access required")
    return current_user


def require_can_request(user: User) -> None:
    """READ_ONLY users may browse/search but not create requests."""
    if user.role == UserRole.READ_ONLY:
        raise HTTPException(
            status_code=403, detail="Your account is read-only and can't make requests."
        )


def user_can_request(user: User, media_type: str) -> bool:
    """Whether a user may search/request a given media type. Admins are never
    restricted; a NULL/empty allowed_media_types means unrestricted; otherwise the
    type must be in the list."""
    if user.role == UserRole.ADMIN:
        return True
    allowed = user.allowed_media_types
    if not allowed:  # None or empty => unrestricted
        return True
    return media_type in allowed


def require_media_type_access(user: User, media_type: str) -> None:
    """Raise 403 if the user isn't allowed to request this media type."""
    if not user_can_request(user, media_type):
        raise HTTPException(
            status_code=403,
            detail=f"You don't have access to request {media_type} items.",
        )


def user_auto_approves(user: User, media_type: str) -> bool:
    """Whether this user's request for a media type should be auto-approved.
    Admins auto-approve their own requests; otherwise the type must be in the
    user's auto_approve_media_types list."""
    if user.role == UserRole.ADMIN:
        return True
    allowed = user.auto_approve_media_types
    return bool(allowed) and media_type in allowed
