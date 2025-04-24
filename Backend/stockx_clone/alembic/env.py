import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import Base
from app.models import (
    users, brand, categories, product, product_variants,
    asks, bids, sales, product_media, sponsored_listings,
    trending_products, watchlist, search_history
)

target_metadata = Base.metadata
