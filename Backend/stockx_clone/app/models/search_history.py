from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    query = Column(Text, nullable=False)
    results_count = Column(Integer)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())