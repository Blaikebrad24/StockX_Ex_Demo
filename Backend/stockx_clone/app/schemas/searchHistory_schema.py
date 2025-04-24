from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class SearchHistoryBase(BaseModel):
    user_id: UUID
    query: str
    results_count: Optional[int]
    category_id: Optional[int]

class SearchHistoryOut(SearchHistoryBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True