from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class AskBase(BaseModel):
    variant_id: int
    seller_id: UUID
    price: float
    condition: str
    status: Optional[str] = "active"
    expires_at: Optional[datetime]
    is_instant: Optional[bool] = False

class AskCreate(AskBase):
    pass

class AskOut(AskBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
