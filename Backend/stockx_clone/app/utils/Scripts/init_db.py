import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from app.database import engine, Base

# ✅ IMPORT ALL MODEL FILES (registers tables with metadata)
from app.models import (
    users, product,sales
)

def create_tables():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully.")

if __name__ == "__main__":
    create_tables()