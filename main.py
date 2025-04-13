import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import customers, networks
from app.core.config import settings

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="API for managing road networks with versioning support",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(networks.router, prefix="/api/networks", tags=["networks"])


@app.get("/")
async def root():
    return {"message": "Welcome to Road Network API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=settings.DEBUG,
    )
