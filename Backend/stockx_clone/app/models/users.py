from sqlalchemy import Column, String, Integer, Boolean, DateTime, DECIMAL, Table, ForeignKey,Enum as SQLAlchemyEnum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import uuid 
from typing import List
from app.database import Base

class RoleEnum(str, Enum):
    FREE_USER = "FREE_USER"
    PAID_USER = "PAID_USER"
    ADMIN = "ADMIN"
    
user_roles = Table(    
    'user_roles',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id')),
    Column('role', String, nullable=False))


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_id = Column(String, unique=True, index=True, nullable=True)  # Optional for custom auth
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password_hash = Column(String, nullable=True)  # For custom auth
    version = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # This avoids the circular reference by using a string for the secondary table
    roles = relationship("UserRole", back_populates="user")
    
    @property
    def role_names(self) -> List[str]:
        """Return a list of role names (strings)"""
        return [role.role for role in self.roles] if self.roles else []
    

# Create a separate UserRole model
class UserRole(Base):
    __tablename__ = "user_role"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    role = Column(String, nullable=False)  # Store as string
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship back to user
    user = relationship("User", back_populates="roles")