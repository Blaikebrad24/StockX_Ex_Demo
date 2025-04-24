from sqlalchemy import Column, String, Boolean, DateTime, DECIMAL 
from sqlalchemy.dialects.postgresql import UUID 
from sqlalchemy.sql import func
import uuid 

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    profile_picture_url = Column(String)
    is_verified = Column(Boolean, default=False)
    seller_rating = Column(DECIMAL(2, 1))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())