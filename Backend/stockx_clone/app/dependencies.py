from fastapi import Depends
import os
import redis
from sqlalchemy.orm import Session
from typing import Generator

from app.database import get_db
from app.service.clerk_service import ClerkService
from app.service.cache_service import CacheService

# Environment variables
CLERK_API_KEY = os.getenv("CLERK_API_KEY", "")
CLERK_WEBHOOK_SECRET = os.getenv("CLERK_WEBHOOK_SECRET", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Redis client
redis_client = redis.from_url(REDIS_URL)

# Initialize services
clerk_service = ClerkService(CLERK_API_KEY)
clerk_service.webhook_secret = CLERK_WEBHOOK_SECRET

cache_service = CacheService(redis_client)

def get_clerk_service() -> ClerkService:
    return clerk_service

def get_cache_service() -> CacheService:
    return cache_service

def get_current_user(clerk_id: str, db: Session = Depends(get_db)):
    """Get the current user from the database"""
    from app.models.user import User
    return db.query(User).filter(User.clerk_id == clerk_id).first()