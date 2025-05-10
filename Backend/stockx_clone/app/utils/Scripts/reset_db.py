# reset_db.py
import psycopg2
import os

# Connection parameters
DB_USER = "stockx"
DB_PASSWORD = "stockx123"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "stockx"

# SQLAlchemy connection string (for reference)
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def reset_database():
    """Reset the database and recreate all tables"""
    print("Connecting to database...")
    
    # Direct connection for dropping tables - use keyword arguments instead of connection string
    conn = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Drop tables if they exist
    print("Dropping existing tables...")
    cursor.execute("DROP TABLE IF EXISTS user_role CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS user_roles CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS users CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS products CASCADE;")
    
    print("Creating tables directly with SQL...")
    
    # Create users table
    cursor.execute("""
    CREATE TABLE users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        clerk_id VARCHAR UNIQUE,
        email VARCHAR UNIQUE NOT NULL,
        name VARCHAR NOT NULL,
        password_hash VARCHAR,
        version INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT TRUE,
        email_verified BOOLEAN DEFAULT FALSE,
        last_login TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """)
    
    # Create index on clerk_id
    cursor.execute("CREATE INDEX idx_users_clerk_id ON users (clerk_id);")
    
    # Create user_role table
    cursor.execute("""
    CREATE TABLE user_role (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        role VARCHAR NOT NULL,
        granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """)
    
    # Create products table
    cursor.execute("""
    CREATE TABLE products (
        id SERIAL PRIMARY KEY,
        name VARCHAR NOT NULL,
        brand VARCHAR,
        model VARCHAR,
        gender VARCHAR,
        condition VARCHAR,
        category VARCHAR,
        listing_type VARCHAR,
        thumbnail_url TEXT,
        description TEXT,
        retail_price DECIMAL(10, 2),
        last_sale_price DECIMAL(10, 2),
        last_sale_date TIMESTAMP WITH TIME ZONE,
        average_price DECIMAL(10, 2),
        sales_count INTEGER DEFAULT 0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """)
    
    conn.close()
    print("Database reset complete!")

if __name__ == "__main__":
    reset_database()