from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models import get_db
from app.models.request import Request

router = APIRouter()


@router.get("/")
async def get_requests(db: Session = Depends(get_db)):
    requests = db.query(Request).all()
    return requests


@router.post("/")
async def create_request(
    title: str, description: str, media_type: str, db: Session = Depends(get_db)
):
    # TODO: Get current user from auth
    request = Request(
        user_id=1,  # Placeholder
        title=title,
        description=description,
        media_type=media_type,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request
