"""
RepoMind Application - Main Entry Point

This module initializes the FastAPI application and registers all API routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.repositories import router as repositories_router
from app.api.routes.diagrams import router as diagrams_router
from app.api.routes.structure import router as structure_router

# Create the FastAPI application
app = FastAPI(
    title="RepoMind API",
    description="API for analyzing GitHub repositories and generating visualizations",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(repositories_router)
app.include_router(diagrams_router)
app.include_router(structure_router)

@app.get("/")
async def root():
    """Root endpoint, returns basic API information."""
    return {
        "name": "RepoMind API",
        "version": "0.1.0",
        "description": "API for analyzing GitHub repositories and generating visualizations",
        "documentation": "/docs"
    } 