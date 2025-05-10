from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
import uuid
from enum import Enum

class RoleEnum(str, Enum):
    FREE_USER = "FREE_USER"
    PAID_USER = "PAID_USER"
    ADMIN = "ADMIN"

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    clerk_id: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    clerk_id: Optional[str] = None
    
    
class UserResponse(UserBase):
    id: uuid.UUID
    clerk_id: Optional[str] = None  # Make sure this is Optional
    roles: List[str] = []  # This should be a list of strings, not UserRole objects

    class Config:
        from_attributes = True

class ClerkUserStatusResponse(BaseModel):
    exists_in_database: bool
    exists_in_clerk: bool
    clerk_id: Optional[str] = None
    user_id: Optional[str] = None
    email: str
    name: Optional[str] = None
    newly_created: Optional[bool] = False
    clerk_id_updated: Optional[bool] = False

class SendMagicLinkRequest(BaseModel):
    email: EmailStr
    redirect_url: str