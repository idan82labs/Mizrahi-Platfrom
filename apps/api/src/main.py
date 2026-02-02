"""
Mizrahi Compliance Platform API

FastAPI application entry point.
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import hooks, jobs, managers, health


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan handler."""
    # Startup
    print("Starting Mizrahi Compliance Platform API...")
    yield
    # Shutdown
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Mizrahi Compliance Platform API",
    description="API for managing regulatory compliance validation hooks",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
cors_origins = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(hooks.router, prefix="/api", tags=["Hooks"])
app.include_router(jobs.router, prefix="/api", tags=["Jobs"])
app.include_router(managers.router, prefix="/api", tags=["Managers"])


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": "Mizrahi Compliance Platform API",
        "version": "1.0.0",
        "status": "ok",
        "docs": "/docs",
    }
