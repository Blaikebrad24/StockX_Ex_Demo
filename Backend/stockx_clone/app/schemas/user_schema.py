# app/schemas/user_schema.py
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    profile_picture_url: Optional[str]

class UserOut(UserBase):
    id: UUID
    is_verified: bool
    seller_rating: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True