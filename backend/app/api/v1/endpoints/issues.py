from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models import get_db
from app.models.issue import Issue, IssueCategory, IssueStatus
from app.models.request import Request, RequestStatus
from app.models.user import User, UserRole
from app.api.v1.deps import get_authenticated_user, get_admin_user

router = APIRouter()


class IssueCreate(BaseModel):
    request_id: int
    category: IssueCategory
    description: str


class IssueUpdate(BaseModel):
    status: Optional[IssueStatus] = None
    admin_response: Optional[str] = None


class IssueResponse(BaseModel):
    id: int
    request_id: int
    request_title: str
    user_id: int
    reporter_email: Optional[str] = None
    category: IssueCategory
    description: str
    status: IssueStatus
    admin_response: Optional[str] = None


def _to_response(issue: Issue, request: Request, reporter: Optional[User]) -> IssueResponse:
    return IssueResponse(
        id=issue.id,
        request_id=issue.request_id,
        request_title=request.title if request else "(deleted)",
        user_id=issue.user_id,
        reporter_email=reporter.email if reporter else None,
        category=issue.category,
        description=issue.description,
        status=issue.status,
        admin_response=issue.admin_response,
    )


@router.post("/", response_model=IssueResponse)
def create_issue(
    body: IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    request = db.query(Request).filter(Request.id == body.request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    # Issues are reported on media you already have.
    if request.status != RequestStatus.FULFILLED:
        raise HTTPException(
            status_code=400,
            detail="Issues can only be reported on fulfilled (available) media",
        )
    # A user may only report on their own request (admins may report on any).
    if current_user.role != UserRole.ADMIN and request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your request")
    if not body.description.strip():
        raise HTTPException(status_code=400, detail="Description is required")

    issue = Issue(
        request_id=request.id,
        user_id=current_user.id,
        category=body.category,
        description=body.description.strip(),
        status=IssueStatus.OPEN,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return _to_response(issue, request, current_user)


@router.get("/", response_model=List[IssueResponse])
def list_issues(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    """Admins see all issues; regular users see only their own."""
    query = db.query(Issue)
    if current_user.role != UserRole.ADMIN:
        query = query.filter(Issue.user_id == current_user.id)
    issues = query.order_by(Issue.created_at.desc()).all()

    # Resolve related rows for the response.
    requests = {r.id: r for r in db.query(Request).all()}
    users = {u.id: u for u in db.query(User).all()}
    return [
        _to_response(i, requests.get(i.request_id), users.get(i.user_id))
        for i in issues
    ]


@router.patch("/{issue_id}", response_model=IssueResponse)
def update_issue(
    issue_id: int,
    body: IssueUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    if body.status is not None:
        issue.status = body.status
    if body.admin_response is not None:
        issue.admin_response = body.admin_response
    db.commit()
    db.refresh(issue)
    request = db.query(Request).filter(Request.id == issue.request_id).first()
    reporter = db.query(User).filter(User.id == issue.user_id).first()
    return _to_response(issue, request, reporter)
