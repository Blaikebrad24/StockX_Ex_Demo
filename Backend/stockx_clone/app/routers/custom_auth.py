from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import uuid

from app.database import get_db
from app.models.users import User, UserRole, RoleEnum
from app.schemas.auth_schema import UserRegister, PasswordReset, PasswordUpdate, Token
from app.schemas.user_schema import UserResponse
from app.utils.auth import (
    get_password_hash, 
    verify_password,
    create_access_token, 
    decode_token,
    create_reset_token,
    verify_reset_token
)
from app.service.email_service import EmailService

router = APIRouter(
    prefix="/api/auth",
    tags=["Custom Auth"]
)

# OAuth2 password flow
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

# Initialize email service
email_service = EmailService()

# Dependency to get current user from token
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current user from the JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Find user in database
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if user is None or not user.is_active:
        raise credentials_exception
    
    return user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """Register a new user with custom authentication"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=hashed_password,
        email_verified=False  # Will be verified later
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Add the FREE_USER role
    user_role = UserRole(
        user_id=user.id,
        role=RoleEnum.FREE_USER.value
    )
    db.add(user_role)
    db.commit()
    
    # Send welcome email
    email_service.send_welcome_email(user.email, user.name)
    
    return user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Get an access token using username/password"""
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login time
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=60 * 24)  # 1 day
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """Get the current authenticated user"""
    # Create a dictionary with the correct structure
    user_data = {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "clerk_id": current_user.clerk_id,
        "roles": current_user.role_names,  # Use the property to get string roles
    }
    return user_data

@router.post("/reset-password")
async def request_password_reset(
    reset_data: PasswordReset,
    request: Request,
    db: Session = Depends(get_db)
):
    """Request a password reset email"""
    user = db.query(User).filter(User.email == reset_data.email).first()
    
    # Don't reveal if user exists or not
    if not user:
        return {"message": "If your email is registered, you will receive a password reset link"}
    
    # Create reset token
    reset_token = create_reset_token(user.id)
    
    # Create reset link
    base_url = str(request.base_url)
    reset_link = f"{base_url}reset-password?token={reset_token}"
    
    # Send email
    email_service.send_password_reset(user.email, reset_link)
    
    return {"message": "If your email is registered, you will receive a password reset link"}

@router.post("/update-password")
async def update_password(
    password_data: PasswordUpdate,
    db: Session = Depends(get_db)
):
    """Update a user's password using a reset token"""
    user_id = verify_reset_token(password_data.token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    # Find user
    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}


# In custom_auth.py
@router.get("/test-custom")
async def test_custom_router():
    return {"message": "Custom auth router is working"}