from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.users import User
from app.schemas.user_schema import UserResponse
from app.middleware.auth import get_clerk_user_id, require_clerk_auth

router = APIRouter(
    prefix="/api/clerk-auth",
    tags=["Clerk Auth"]
)

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user_id: str = Depends(require_clerk_auth),
    db: Session = Depends(get_db)
):
    """Get the current authenticated user"""
    user = db.query(User).filter(User.clerk_id == current_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/validate")
async def validate_token(request: Request):
    """Validate the authentication token"""
    user_id = await get_clerk_user_id(request)
    return {"authenticated": user_id is not None, "user_id": user_id}


@router.get("/test-clerk")
async def test_clerk_router():
    return {"message": "Clerk auth router is working"}

