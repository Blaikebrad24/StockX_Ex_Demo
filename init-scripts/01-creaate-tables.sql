CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    profile_picture_url TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    seller_rating DECIMAL(2,1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE brands (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    logo_url TEXT,
    is_featured BOOLEAN DEFAULT FALSE,
    category_preference VARCHAR(50)
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    parent_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(name, parent_id)
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id) ON DELETE CASCADE,
    primary_category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    style_id VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    release_date DATE,
    colorway VARCHAR(100),
    retail_price DECIMAL(10, 2),
    gender VARCHAR(20),
    thumbnail_url TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_sale_price DECIMAL(10, 2),
    last_sale_date TIMESTAMP WITH TIME ZONE,
    sales_count INTEGER DEFAULT 0
);

CREATE TABLE product_variants (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    size VARCHAR(20),
    color VARCHAR(50),
    sku VARCHAR(100),
    UNIQUE(product_id, size, color)
);

CREATE TABLE asks (
    id SERIAL PRIMARY KEY,
    variant_id INTEGER REFERENCES product_variants(id) ON DELETE CASCADE,
    seller_id UUID REFERENCES users(id) ON DELETE CASCADE,
    price DECIMAL(10, 2) NOT NULL,
    condition VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    expires_at TIMESTAMP WITH TIME ZONE,
    is_instant BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE bids (
    id SERIAL PRIMARY KEY,
    variant_id INTEGER REFERENCES product_variants(id) ON DELETE CASCADE,
    buyer_id UUID REFERENCES users(id) ON DELETE CASCADE,
    price DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    variant_id INTEGER REFERENCES product_variants(id) ON DELETE SET NULL,
    ask_id INTEGER REFERENCES asks(id) ON DELETE SET NULL,
    bid_id INTEGER REFERENCES bids(id) ON DELETE SET NULL,
    seller_id UUID REFERENCES users(id) ON DELETE SET NULL,
    buyer_id UUID REFERENCES users(id) ON DELETE SET NULL,
    sale_price DECIMAL(10, 2) NOT NULL,
    sale_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    stripe_payment_intent_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'completed'
);

CREATE TABLE product_media (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    media_url TEXT NOT NULL,
    media_type VARCHAR(20) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    position INTEGER DEFAULT 0,
    caption VARCHAR(255)
);

CREATE TABLE sponsored_listings (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    sponsor_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE trending_products (
    product_id INTEGER PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
    score DECIMAL(10, 2) NOT NULL,
    trend_direction VARCHAR(10),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE watchlist (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    variant_id INTEGER REFERENCES product_variants(id) ON DELETE CASCADE,
    desired_price DECIMAL(10, 2),
    notify_on_price BOOLEAN DEFAULT FALSE,
    notify_on_restock BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, variant_id)
);

CREATE TABLE search_history (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    results_count INTEGER,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);