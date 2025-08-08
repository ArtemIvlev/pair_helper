from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.core.database import engine
from app.models import Base

# Create database tables (commented out for now)
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pair Helper API",
    description="API для Telegram Web App для пар",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted hosts middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Pair Helper API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
