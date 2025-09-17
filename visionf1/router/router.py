"""
Router definitions for VisionF1 endpoints.
"""

import logging
from fastapi import APIRouter
from visionf1.controller.controller import get_driver_standings_controller
from visionf1.models.models import DriverStandingsResponse

logger = logging.getLogger(__name__)


router = APIRouter()

logger.info("Registering router endpoints...")

@router.get("/driver-standings", response_model=DriverStandingsResponse, status_code=200, tags=["GET /driver-standings"])
async def get_driver_standings_endpoint():
    """
    Routes GET /driver-standings endpoint.
    """
    logger.info("GET /driver-standings endpoint called.")
    return get_driver_standings_controller()
