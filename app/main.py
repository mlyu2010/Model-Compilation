"""
FastAPI main application module for ML model compilation and deployment.

This module provides the main FastAPI application instance with endpoints for
compiling ML models using Apache TVM and OpenXLA frameworks.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import compilation, inference, models

app = FastAPI(
    title="Model Compilation API",
    description="ML Compiler API for deploying BrainChip's Akida TENNs models using TVM and OpenXLA",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(compilation.router, prefix="/api/v1", tags=["compilation"])
app.include_router(inference.router, prefix="/api/v1", tags=["inference"])
app.include_router(models.router, prefix="/api/v1", tags=["models"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Model Compilation API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
