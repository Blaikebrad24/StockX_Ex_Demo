from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models.product import Base  # Import Base specifically
from app.routers import products  # Import the products router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StockX Clone API",
    description="API for a StockX-like marketplace",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to StockX Clone API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}