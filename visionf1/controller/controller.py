"""
Controller handles request validation, response formatting, and interaction with services.
"""

import logging
from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from visionf1.models.models import ErrorResponse
from visionf1.service.service import obtain_driver_standings
from visionf1.models.models import DriverStandingsResponse

logger = logging.getLogger(__name__)


def get_driver_standings_controller() -> DriverStandingsResponse:
    """
    Retrieves driver standings.
    """
    logger.info("Retrieving driver standings...")
    driver_standings = obtain_driver_standings()
    logger.debug(f"Driver standings retrieved: {driver_standings}")
    return DriverStandingsResponse(data=driver_standings)
