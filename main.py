"""
Main entry point for VisionF1 Content Service API.
Sets up FastAPI app, router, and exception handlers.
"""

import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
