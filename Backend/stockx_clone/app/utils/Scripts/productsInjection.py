import json
import os 
from datetime import datetime 
from typing import List, Optional
from uuid import UUID 
from glob import glob 
import multiprocessing

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pydantic import BaseModel, validator 
from product import Product 

DATABASE_URL = "postgresql://stockx:stockx123@localhost:5432/stockx"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class ProductSchema(BaseModel):
    id: UUID
    name: str
    title: Optional[str]
    description: Optional[str]
    brand: Optional[str]
    model: Optional[str]
    gender: Optional[str]
    condition: Optional[str]
    category: Optional[str]
    listing_type: Optional[str]
    thumbnail_url: Optional[str]
    retail_price: Optional[int]
    last_sale_price: Optional[int]
    last_sale_date: Optional[datetime]
    average_price: Optional[int]
    sales_count: Optional[int]

    @validator('last_sale_date', pre=True)
    def parse_datetime(cls, v):
        if v is None:
            return None
        return datetime.fromisoformat(v.replace('Z', '+00:00'))
    

def extract_product_data(item: dict) -> dict:
    product_traits = {trait['name']: trait['value'] for trait in item.get('productTraits', [])}

    market = item.get('market', {})
    sales_info = market.get('salesInformation', {})
    statistics = market.get('statistics', {}).get('annual', {})

    return {
        "id": item.get('objectId'),
        "name": item.get('name'),
        "title": item.get('title'),
        "description": item.get('description'),
        "brand": item.get('brand'),
        "model": item.get('model'),
        "gender": item.get('gender'),
        "condition": item.get('condition'),
        "category": item.get('productCategory'),
        "listing_type": item.get('listingType'),
        "thumbnail_url": item.get('media', {}).get('thumbUrl'),
        "retail_price": int(product_traits.get('Retail Price', 0)) if product_traits.get('Retail Price') else None,
        "last_sale_price": sales_info.get('lastSale'),
        "last_sale_date": sales_info.get('lastSaleDate'),
        "average_price": statistics.get('averagePrice'),
        "sales_count": statistics.get('salesCount')
    }
    

def parse_json_file(json_path: str) -> List[ProductSchema]:
    with open(json_path, 'r') as file:
        content = json.load(file)
        results = content['data']['results']
        cleaned = []
        for item in results:
            product_data = extract_product_data(item)
            validated = ProductSchema(**product_data)
            cleaned.append(validated)
        return cleaned


def bulk_insert_products(products: List[ProductSchema]):
    session = SessionLocal()
    try:
        db_objects = [Product(**product.dict()) for product in products]
        session.bulk_save_objects(db_objects)
        session.commit()
    except Exception as e:
        print(f"Error inserting products: {e}")
        session.rollback()
    finally:
        session.close()

# ---------- Multiprocessing + TQDM ----------
def main():
    json_files = glob('./*.json')  # Adjust path if needed

    all_products = []
    with multiprocessing.Pool(processes=os.cpu_count()) as pool:
        # tqdm wraps the pool.imap for progress tracking
        for product_batch in tqdm(pool.imap(parse_json_file, json_files), total=len(json_files), desc="Parsing JSON Files"):
            all_products.extend(product_batch)

    print(f"✅ Total products parsed: {len(all_products)}")
    bulk_insert_products(all_products)
    print("✅ All products inserted into the database!")

if __name__ == "__main__":
    main()