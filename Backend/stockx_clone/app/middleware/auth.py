from fastapi import Depends, HTTPException, Request, status
from typing import Optional
import jwt
from datetime import datetime
import os

from app.dependencies import get_clerk_service

# Get Clerk public key from environment
CLERK_JWT_KEY = os.getenv("CLERK_JWT_KEY", "")

async def get_clerk_user_id(request: Request) -> Optional[str]:
    """Extract and validate the Clerk user ID from the request"""
    # Try session cookie first
    session_token = request.cookies.get("__session")
    
    # If no cookie, try Authorization header
    if not session_token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            session_token = auth_header[7:]
    
    if not session_token:
        return None
    
    try:
        # Verify the JWT token
        decoded = jwt.decode(
            session_token,
            CLERK_JWT_KEY,
            algorithms=["RS256"],
            audience="fastapi-app",  # Set your app name here
            options={"verify_exp": True}
        )
        
        # Extract user ID
        user_id = decoded.get("sub")
        if not user_id:
            return None
        
        return user_id
    
    except Exception as e:
        print(f"Token validation error: {str(e)}")
        return None

async def require_clerk_auth(request: Request):
    """Middleware that requires Clerk authentication"""
    user_id = await get_clerk_user_id(request)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user_id