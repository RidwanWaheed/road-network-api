import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import os
from app.core.config import settings
from app.api.endpoints import customers, networks

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="API for managing road networks with versioning support"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API endpoints
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(networks.router, prefix="/api/networks", tags=["networks"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Road Network API"}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=settings.DEBUG
    )