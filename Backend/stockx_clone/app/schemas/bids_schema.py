from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class BidBase(BaseModel):
    variant_id: int
    buyer_id: UUID
    price: float
    status: Optional[str] = "active"
    expires_at: Optional[datetime]

class BidCreate(BidBase):
    pass

class BidOut(BidBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
