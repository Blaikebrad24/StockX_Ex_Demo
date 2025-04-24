from sqlalchemy import Column, String, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID 
from app.database import Base


class Brand(Base):
    __tablename__ = "brands"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(String)
    logo_url = Column(String)
    is_featured = Column(Boolean, default=False)
    catergory_preference = Column(String(50))
    