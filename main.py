"""FinWise-AI: Multimodal RAG-Enhanced AI Assistant for Financial Document Analysis

Main application entry point with FastAPI backend.
"""

import os
import sys
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FinWise-AI",
    description="Multimodal RAG-Enhanced AI Assistant for Financial Document Analysis",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting FinWise-AI application...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    # Try to import and initialize services
    try:
        # Import will work once we create the files
        from src.api.routes import router as api_router
        app.include_router(api_router, prefix="/api/v1")
        logger.info("API routes loaded successfully")
    except ImportError as e:
        logger.warning(f"Could not load API routes: {e}")
        logger.info("Run setup script to create all necessary files")
    
    # Initialize MLflow if configured
    mlflow_uri = os.getenv('MLFLOW_TRACKING_URI')
    if mlflow_uri:
        try:
            import mlflow
            mlflow.set_tracking_uri(mlflow_uri)
            logger.info(f"MLflow tracking URI: {mlflow_uri}")
        except ImportError:
            logger.warning("MLflow not installed")
    
    logger.info("FinWise-AI application started successfully!")
    logger.info("Access API docs at: http://localhost:8000/api/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down FinWise-AI application...")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to FinWise-AI",
        "description": "Multimodal RAG-Enhanced AI Assistant for Financial Document Analysis",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": os.getenv('ENVIRONMENT', 'development'),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'true').lower() == 'true'
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )