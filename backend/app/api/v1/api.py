from fastapi import APIRouter
from app.api.v1.endpoints import auth, requests, users, admin, metadata

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(requests.router, prefix="/requests", tags=["requests"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(metadata.router, prefix="/metadata", tags=["metadata"])
