from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product
from app.schemas.product import ProductResponse
from typing import List

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.get("/trending", response_model=List[ProductResponse])
def get_trending_products(db: Session = Depends(get_db)):
    products = db.query(Product).order_by(Product.sales_count.desc()).limit(20).all()
    return products

@router.get("/popular-brands", response_model=List[ProductResponse])
def get_popular_brands(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.brand.isnot(None)).order_by(Product.brand.asc()).limit(20).all()
    return products

@router.get("/new-arrivals", response_model=List[ProductResponse])
def get_new_arrivals(db: Session = Depends(get_db)):
    products = db.query(Product).order_by(Product.created_at.desc()).limit(20).all()
    return products