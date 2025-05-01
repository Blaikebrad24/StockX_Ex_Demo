# Product Import Script Overview: 
#   - Script takes JSON data from different sources with varying structures, parses it 
#   - consistent format and imports product data into Postgres
#
# Core Components :
#   - Database connection: uses SQLAlchemy to connect to postgres database instance
#   - Data validation: uses Pydantic to validate data before database insertion
#   - Parsing logic: Contains specialized parsers for different JSON structures
#   - Multiprocessing: process multiple files concurrently for a better performance 
#
# Steps: 
#   - Data schema validation -> defining a Pydantic model (ProductSchema) that mirrors SQLAlchemy db model 'product.py'
#   - Format Specific Parsers -> 1. Adidas parser handles nested structures with 'market.salesInformation'
#                                2. New Balance parser handles flatter structure with direct properties
#
#   - Format detection: 'detect_and_parse_json_item' function examines each JSON item item to determine format it follows
#   - File processiong: each JSON file within /utils/Data/**/*.json is processed with defensive error handling
#   - Parallel processing: scripit uses Python mulitprocessing files concurrently
#   - Database insertion: insert processed product data into products table 
#
#   update: Pydantic version to LTS
#
#


import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from decimal import Decimal
from glob import glob
import multiprocessing
from tqdm import tqdm

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pydantic import BaseModel, Field, validator
from app.models.product import Product

DATABASE_URL = "postgresql://stockx:stockx123@localhost:5432/stockx"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class ProductSchema(BaseModel):
    """Pydantic model to validate product data before database insertion"""
    name: str
    brand: Optional[str] = None
    model: Optional[str] = None
    gender: Optional[str] = None
    condition: Optional[str] = None
    category: Optional[str] = None
    listing_type: Optional[str] = None
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    retail_price: Optional[Decimal] = None
    last_sale_price: Optional[Decimal] = None
    last_sale_date: Optional[datetime] = None
    average_price: Optional[Decimal] = None
    sales_count: Optional[int] = 0

    # Continue using validator for Pydantic V1 compatibility
    @validator('last_sale_date', pre=True)
    def parse_datetime(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            try:
                # Handle ISO format strings with timezone
                if 'Z' in v:
                    return datetime.fromisoformat(v.replace('Z', '+00:00'))
                # Handle date-only strings (like release dates)
                if len(v.split('-')) == 3 and 'T' not in v:
                    return datetime.strptime(v, '%Y-%m-%d')
                return datetime.fromisoformat(v)
            except (ValueError, TypeError):
                return None
        return v

    @validator('retail_price', 'last_sale_price', 'average_price', pre=True)
    def convert_to_decimal(cls, v):
        if v is None:
            return None
        try:
            return Decimal(str(v))
        except (ValueError, TypeError):
            return None

def parse_adidas_json(item: Dict[str, Any]) -> Dict[str, Any]:
    """Parse Adidas apparel structured JSON"""
    # Check if item is a string (which would cause errors)
    if isinstance(item, str):
        return {"name": "Invalid item", "description": "Item was a string"}
    
    product_traits = {}
    if item.get('productTraits') and isinstance(item['productTraits'], list):
        product_traits = {trait['name']: trait['value'] for trait in item['productTraits']}

    market = item.get('market', {})
    sales_info = market.get('salesInformation', {})
    statistics = market.get('statistics', {}).get('annual', {})
    media = item.get('media', {})

    # Ensure we have a valid name
    name = item.get('name') or item.get('title', '')
    if not name:
        name = "Unknown Product"

    return {
        "name": name,
        "brand": item.get('brand'),
        "model": item.get('model'),
        "gender": item.get('gender'),
        "condition": item.get('condition'),
        "category": item.get('productCategory'),
        "listing_type": item.get('listingType'),
        "thumbnail_url": media.get('thumbUrl') or media.get('smallImageUrl') if isinstance(media, dict) else None,
        "description": item.get('description'),
        "retail_price": float(product_traits.get('Retail Price', 0)) if product_traits.get('Retail Price') else None,
        "last_sale_price": sales_info.get('lastSale'),
        "last_sale_date": sales_info.get('lastSaleDate'),
        "average_price": statistics.get('averagePrice'),
        "sales_count": statistics.get('salesCount')
    }

def parse_newbalance_json(item: Dict[str, Any]) -> Dict[str, Any]:
    """Parse New Balance sneaker structured JSON"""
    # Check if item is a string (which would cause errors)
    if isinstance(item, str):
        return {"name": "Invalid item", "description": "Item was a string"}
        
    # Ensure we have a valid name
    name = item.get('shoeName', '')
    if not name:
        name = "Unknown Sneaker"
        
    return {
        "name": name,
        "brand": item.get('brand'),
        "model": item.get('make') or item.get('silhoutte'),
        "gender": None,  # Not provided in this format
        "condition": "New",  # Assuming new condition for all shoes
        "category": "sneakers",  # Default category for this format
        "listing_type": "STANDARD",  # Default listing type
        "thumbnail_url": item.get('thumbnail'),
        "description": item.get('description'),
        "retail_price": item.get('retailPrice'),
        "last_sale_price": item.get('lowestResellPrice', {}).get('stockX') if isinstance(item.get('lowestResellPrice'), dict) else None,
        "last_sale_date": item.get('releaseDate'),
        "average_price": None,  # Not provided in this format
        "sales_count": 0  # Default as not provided
    }

def detect_and_parse_json_item(item: Any) -> Dict[str, Any]:
    """Detect the JSON structure type and parse accordingly"""
    # Check if item is valid
    if not isinstance(item, dict):
        print(f"⚠️ Invalid item type: {type(item)}")
        return {"name": f"Invalid item type: {type(item)}"}
    
    # If it has objectId or title fields, it's likely the Adidas format
    if "objectId" in item or "title" in item:
        return parse_adidas_json(item)
    # If it has shoeName, it's likely the New Balance format
    elif "shoeName" in item:
        return parse_newbalance_json(item)
    # If we can't determine the format, return a minimal dict
    else:
        print(f"⚠️ Unknown item format: {item.keys() if hasattr(item, 'keys') else 'Not a dict'}")
        return {"name": "Unknown Product"}

def parse_json_file(json_path: str) -> List[ProductSchema]:
    """Parse a JSON file and return a list of validated ProductSchema objects"""
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            content = json.load(file)

        # Handle different JSON structures
        results = []
        if isinstance(content, dict) and 'data' in content:
            data = content['data']
            if isinstance(data, dict) and 'results' in data:
                results = data['results']
        elif isinstance(content, list):
            # New Balance format - direct list
            results = content
        else:
            print(f"⚠️ Unrecognized JSON format in file: {json_path}")
            return []

        cleaned = []
        for idx, item in enumerate(results):
            try:
                if item is None:  # Skip empty items
                    continue
                
                # Detect and parse based on structure
                product_data = detect_and_parse_json_item(item)
                
                # Validate with Pydantic model
                validated = ProductSchema(**product_data)
                cleaned.append(validated)
            except Exception as e:
                print(f"❗ Skipping invalid item in {json_path} at index {idx}: {e}")
                continue
                
        print(f"✅ Parsed {len(cleaned)} products from {json_path}")
        return cleaned
    except Exception as e:
        print(f"❌ Error processing file {json_path}: {e}")
        return []

def bulk_insert_products(products: List[ProductSchema]):
    """Insert multiple products into the database"""
    if not products:
        print("No products to insert")
        return
        
    session = SessionLocal()
    try:
        # Convert Pydantic models to SQLAlchemy models
        db_objects = []
        for product in products:
            # Continue using dict() for Pydantic V1
            product_dict = product.dict()
            db_objects.append(Product(**product_dict))
            
        session.bulk_save_objects(db_objects)
        session.commit()
        print(f"✅ Successfully inserted {len(db_objects)} products")
    except Exception as e:
        print(f"❌ Error inserting products: {e}")
        session.rollback()
    finally:
        session.close()

def process_file(json_path: str) -> List[ProductSchema]:
    """Process a single JSON file and return validated products"""
    return parse_json_file(json_path)

def main():
    """Main function to process all JSON files and insert them into the database"""
    # Find all JSON files in the data directory
    json_files = glob('./app/utils/Data/**/*.json', recursive=True)
    
    if not json_files:
        print("⚠️ No JSON files found! Check your directory path.")
        return
        
    print(f"Found {len(json_files)} JSON files to process")
    
    # Process files with multiprocessing
    all_products = []
    with multiprocessing.Pool(processes=max(1, os.cpu_count() - 1)) as pool:
        # Use tqdm to show progress
        results = list(tqdm(
            pool.imap(process_file, json_files),
            total=len(json_files),
            desc="Processing JSON Files"
        ))
        
        # Flatten the list of lists
        for product_batch in results:
            all_products.extend(product_batch)

    print(f"✅ Total products parsed: {len(all_products)}")
    
    # Insert all products into the database
    if all_products:
        bulk_insert_products(all_products)
        print("✅ All products inserted into the database!")
    else:
        print("⚠️ No valid products found to insert.")

if __name__ == "__main__":
    main()