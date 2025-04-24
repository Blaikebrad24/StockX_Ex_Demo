from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class WatchlistBase(BaseModel):
    user_id: UUID
    variant_id: int
    desired_price: Optional[float]
    notify_on_price: Optional[bool] = False
    notify_on_restock: Optional[bool] = False

class WatchlistOut(WatchlistBase):
    created_at: datetime

    class Config:
        orm_mode = True