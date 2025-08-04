"""
Main FastAPI Application for AICK Studio Abandoned Cart Recovery Agent

This module sets up the FastAPI application with all routes, middleware,
and configuration for the abandoned cart recovery system.
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    """
    logger.info("Starting AICK Studio Abandoned Cart Recovery Agent")
    
    # Startup logic
    try:
        # Initialize any required services here
        logger.info("Application startup completed")
        yield
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        raise
    finally:
        # Shutdown logic
        logger.info("Application shutdown completed")


# Create FastAPI application
app = FastAPI(
    title="AICK Studio Abandoned Cart Recovery Agent",
    description="Agentic AI solution for recovering abandoned shopping carts using LangGraph",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from .routes.agent import router as agent_router
from .routes.dashboard import router as dashboard_router
from .routes.webhooks import router as webhook_router

app.include_router(agent_router, prefix="/api/agent", tags=["Agent"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(webhook_router, prefix="/api/webhooks", tags=["Webhooks"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "AICK Studio Abandoned Cart Recovery Agent",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with basic information
    """
    return {
        "message": "AICK Studio Abandoned Cart Recovery Agent",
        "version": "1.0.0",
        "docs": "/api/docs",
        "dashboard": "/dashboard"
    }

# Serve static files (for production deployment)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve frontend (for production deployment)
if os.path.exists("frontend/dist"):
    app.mount("/dashboard", StaticFiles(directory="frontend/dist", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )

