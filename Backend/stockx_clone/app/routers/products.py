from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.product import Product
from app.schemas.product_schema import ProductResponse, ProductCreate, ProductUpdate
from typing import List, Optional

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

# Existing Routes with minor improvements

@router.get("/trending", response_model=List[ProductResponse])
def get_trending_products(limit: int = Query(20, description="Number of products to return"), db: Session = Depends(get_db)):
    
    """Get trending products based on sales count."""
    products = db.query(Product).filter(Product.sales_count.isnot(None))\
                .order_by(Product.sales_count.desc())\
                .limit(limit).all()
    return products

@router.get("/popular-brands", response_model=List[ProductResponse])
def get_popular_brands(limit: int = Query(20, description="Number of products to return"),db: Session = Depends(get_db)):
    """Get products from the most popular brands."""
    products = db.query(Product)\
                .filter(Product.brand.isnot(None))\
                .order_by(Product.brand.asc())\
                .limit(limit).all()
    return products

@router.get("/new-arrivals", response_model=List[ProductResponse])
def get_new_arrivals(limit: int = Query(20, description="Number of products to return"),db: Session = Depends(get_db)):
    """Get the most recently added products."""
    products = db.query(Product)\
                .order_by(Product.created_at.desc())\
                .limit(limit).all()
    return products

# New Routes

#TODO - not responding back with data, empty object array
@router.get("/recommended-for-you", response_model=List[ProductResponse])
def get_recommended_products(category: Optional[str] = Query(None, description="Filter by product category"),brand: Optional[str] = Query(None, description="Filter by brand"),gender: Optional[str] = Query(None, description="Filter by gender (men, women, unisex)"),limit: int = Query(20, description="Number of products to return"),db: Session = Depends(get_db)):
    """
    Get personalized product recommendations.
    
    This endpoint returns products based on category, brand, and gender preferences.
    It prioritizes products with higher sales and good pricing relative to retail.
    """
    query = db.query(Product)
    
    # Apply filters if provided
    if category:
        query = query.filter(Product.category == category)
    if brand:
        query = query.filter(Product.brand == brand)
    if gender:
        query = query.filter(Product.gender == gender)
    
    # Create a dynamic ordering based on sales count and price/retail ratio
    # This will recommend popular items with good value
    query = query.filter(Product.retail_price.isnot(None), Product.last_sale_price.isnot(None))
    
    # Order by a combination of factors: sales count and value
    products = query.order_by(
        Product.sales_count.desc(),
        (Product.retail_price - Product.last_sale_price).desc()
    ).limit(limit).all()
    
    return products

@router.get("/three-day-shipping", response_model=List[ProductResponse])
def get_three_day_shipping(limit: int = Query(20, description="Number of products to return"),db: Session = Depends(get_db)):
    """
    Get products eligible for three-day shipping.
    
    This endpoint returns products that are available for quick shipping,
    prioritizing popular items with high sales counts.
    """
    # For this example, we'll use products with higher sales as a proxy
    # for items that might be in stock for quick shipping
    products = db.query(Product)\
                .filter(Product.sales_count > 10)\
                .order_by(Product.sales_count.desc())\
                .limit(limit).all()
    
    return products

# CRUD Operations

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product."""
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a product by ID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return product

@router.get("/", response_model=List[ProductResponse])
def get_products(skip: int = Query(0, description="Number of records to skip"),limit: int = Query(100, description="Number of records to return"), brand: Optional[str] = Query(None, description="Filter by brand"),category: Optional[str] = Query(None, description="Filter by category"),gender: Optional[str] = Query(None, description="Filter by gender"), min_price: Optional[float] = Query(None, description="Minimum price"),max_price: Optional[float] = Query(None, description="Maximum price"),db: Session = Depends(get_db)):
    """
    Get products with optional filtering.
    
    This endpoint allows filtering by various product attributes.
    """
    query = db.query(Product)
    
    # Apply filters if provided
    if brand:
        query = query.filter(Product.brand == brand)
    if category:
        query = query.filter(Product.category == category)
    if gender:
        query = query.filter(Product.gender == gender)
    if min_price is not None:
        query = query.filter(Product.last_sale_price >= min_price)
    if max_price is not None:
        query = query.filter(Product.last_sale_price <= max_price)
    
    # Apply pagination
    products = query.order_by(Product.id).offset(skip).limit(limit).all()
    return products

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int,product: ProductUpdate,db: Session = Depends(get_db)):
    """Update a product by ID."""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    # Update model with provided values, skipping None values
    update_data = product.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product by ID."""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    db.delete(db_product)
    db.commit()
    return None

@router.get("/search/{query}", response_model=List[ProductResponse])
def search_products(query: str,limit: int = Query(20, description="Number of products to return"),db: Session = Depends(get_db)):
    """
    Search products by name, brand, or description.
    
    This endpoint performs a case-insensitive search across multiple product fields.
    """
    search_term = f"%{query}%"
    products = db.query(Product).filter(
        (Product.name.ilike(search_term)) |
        (Product.brand.ilike(search_term)) |
        (Product.description.ilike(search_term)) |
        (Product.model.ilike(search_term))
    ).limit(limit).all()
    
    return products