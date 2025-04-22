[#][#][#]Backend Rough draft design doc[#][#][#]


[statement] - This document will serve as the rough draft and index of the StockX backend application notes etc during development 

*** Building a complete and robust backend API ***
  [#] Python, 
  [#] Postgresql (Raw SQL & SQLAlchemy)
  [#] Alembic database migration 
  [#] Postman/ThunderClient
  [#] Testing
  [#] Deployment to an Ubuntu machine 
                [#]hosted in AWS
                [#]Nginx reverse proxy 
                [#] SystemD service
                [#] Configure Firewall
                [#] Setup SSL for Http traffic
  [#] Deploy on Heroku (if Cloud provider is not an option)
  [#] Dockerize API for Deployment
  [#] Build CI/CD pipeline using Github Actions

[#][#]Build Steps [#][#] 
    1. Design Postgres Database based off StockX current UI
    [#][#][#] Database Design [#][#][#]
        - Create necessary indexes for database tables
        PostgreSQL Tables: 
        [#] Users, Brands, Categories, Products, Product_Variants,Asks, Bids, Sales, Product_Media,
            Sponsored_Listings, Trending_Products,Watchlist,Search History

        [#] Create TABLE Examples
        users(
                id UUID PRIMARY KEY,  -- Matches Clerk user ID
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                profile_picture_url TEXT,
                is_verified BOOLEAN DEFAULT FALSE,
                seller_rating DECIMAL(2,1),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        brands (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    slug VARCHAR(100) UNIQUE NOT NULL,
                    description TEXT,
                    logo_url TEXT,
                    is_featured BOOLEAN DEFAULT FALSE,
                    category_preference VARCHAR(50)  -- 'sneakers', 'apparel', 'watches', etc.
               );

    [#][#][#] End Database Design [#][#][#]

    2. Pull and Startup Docker Container (Postgres)
    [#][#][#] Docker Container [#][#][#]
        - Pull latest Postgres Image from Docker 
        - Create StockX Postgres database using Docker commands
    [#][#][#] Docker Container End Instructions[#][#][#]

    2a. Create docker-compose for container services for local Testing
    [#][#][#] create docker-compose file on top level to run containers [#][#][#]

    [#][#][#] create docker-compose file on top level to run containers [#][#][#]
    
    
    3. Compose & Create a 'MockData.json' file to store entire StockX data 
    [#][#][#] Find and Store StockX Products - dummy products[#][#][#]
        - Find StockX products, Sneakers and other apparel API from 'RapidAPI'
        - Customize and form the response from Rapid API to follow StockX-Demo Postgres Database schema
    [#][#][#] Find and Store StockX Products - dummy products[#][#][#]

    4. Create Service/Business Logic Layer within FastAPI
    [#][#][#] Configure and Setup FastAPI | Create Business/Service layer logic for StockX [#][#][#]
        - Database connection with SQLAlchemy
        - Create Database schema/models
        - Create Pydantic schemas for data validation
        - Create CRUD methods for each Postgres Table 
        - Setup FastAPI folder structure etc if needed in Vscode
        - Create service layer and business logic classes utilizng SQLAlchemy for ORM purposes
        - Create http route handlers/controllers for front invocation and Test using Postman/ThunderClient
        - Integrate Reids Cache or Elasticache using Docker Container

    [#][#][#] Configure and Setup FastAPI | Create Business/Service layer logic for StockX [#][#][#]

    5. Implement Security - FastAPI | OAuth2 with JWT
    [#][#][#] TLS/HTTPS Implementation [#][#][#]
        [#] For local - development[#]
            - Create self-signed certificate using openssl
            - Configure FastAPI with SSL
            - Speciy 'Docker volumes' to point to created .pem files
            - Integrate OAuth with JWT with FastAPI
            - Integrate FastAPI with Clerk (verify/validate Clerk JWTs)
            - Implement standalone JWT verification
        [#] For local - development[#]

        [#] For AWS Lambda Deployment [#]
            - AWS gateway in front of Lambda 
            - Create custom domain with ACM certificate
            - Enforce TLS 1.2+ in API Gateway
        [#] For AWS Lambda Deployment [#]
    [#][#][#] TLS/HTTPS Implementation [#][#][#]

    6. CI/CD | Github Actions | API Testing