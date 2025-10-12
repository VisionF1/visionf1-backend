"""
Main entry point for VisionF1 Content Service API.
Sets up FastAPI app, router, and exception handlers.
"""

import logging
import os
from fastapi import FastAPI
from visionf1.router.router import router as course_router

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



app = FastAPI(
    title = "VisionF1 Content Service API",
    version = "1.0.0",
)

logger.info("Including routers...")
app.include_router(course_router)

logger.info("Application setup complete.")
