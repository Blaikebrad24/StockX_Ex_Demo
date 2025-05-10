from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import product, users  # Import both models
from app.routers import products, clerk_webhook, auth, custom_auth

# Create database tables
product.Base.metadata.create_all(bind=engine)
users.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StockX Clone API",
    description="API for a StockX-like marketplace with user authentication",
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
app.include_router(clerk_webhook.router)
app.include_router(auth.router, prefix="", tags=["Clerk Auth"])
app.include_router(custom_auth.router, prefix="", tags=["Custom Auth"])


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to StockX Clone API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}