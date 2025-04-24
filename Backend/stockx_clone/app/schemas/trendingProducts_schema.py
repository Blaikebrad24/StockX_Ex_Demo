from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TrendingProductBase(BaseModel):
    product_id: int
    score: float
    trend_direction: Optional[str]

class TrendingProductOut(TrendingProductBase):
    updated_at: datetime

    class Config:
        orm_mode = True