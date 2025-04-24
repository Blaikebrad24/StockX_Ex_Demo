from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SponsoredListingBase(BaseModel):
    product_id: int
    start_date: datetime
    end_date: datetime
    is_active: Optional[bool] = True
    priority: Optional[int] = 0
    sponsor_name: Optional[str]

class SponsoredListingOut(SponsoredListingBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True