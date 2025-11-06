"""
Main entry point for VisionF1 Content Service API.
Sets up FastAPI app, router, and exception handlers.
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from visionf1.router.router import router as course_router
from visionf1.ml.model_loader import ModelLoader
from visionf1.ml.race_predictor import CachedRacePredictor

environment = os.getenv('ENVIRONMENT', 'development')

log_level = logging.DEBUG if environment == 'development' else logging.INFO
logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=log_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
logging.getLogger("pymongo").setLevel(logging.WARNING) # Reduce pymongo logging verbosity
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup/shutdown events."""
    logger.info("🚀 Application startup...")
    
    # Download ML artifacts from Cloudinary
    try:
        loader = ModelLoader(cache_dir="./model_cache")
        paths = loader.download_all_artifacts()
        
        # Initialize predictor
        predictor = CachedRacePredictor()
        predictor.initialize(
            model_path=paths["model"],
            history_path=paths["history_store"],
            features_path=paths["feature_names"]
        )
        
        logger.info("✅ ML predictor ready")
    except Exception as e:
        logger.error(f"Failed to initialize ML predictor: {e}")
        # raise  # Uncomment to force shutdown if it fails
    
    yield  # App runs here
    
    logger.info("Application shutdown...")

app = FastAPI(
    title = "VisionF1 Content Service API",
    version = "1.0.0",
    lifespan = lifespan
)

allowed_origins = [
    "http://localhost:3000",  # Next.js dev server
    "https://visionf1.vercel.app", # Production frontend
    "https://visionf1.app" # Production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

logger.info("Including routers...")
app.include_router(course_router)

logger.info("Application setup complete.")
