from pydantic import BaseModel
from typing import Optional

class BrandBase(BaseModel):
    name: str
    slug: str

class BrandCreate(BrandBase):
    description: Optional[str] = None
    logo_url: Optional[str] = None
    is_featured: Optional[bool] = False
    category_preference: Optional[str] = None

class BrandOut(BrandBase):
    id: int
    description: Optional[str]
    logo_url: Optional[str]
    is_featured: Optional[bool]
    category_preference: Optional[str]

    class Config:
        orm_mode = True