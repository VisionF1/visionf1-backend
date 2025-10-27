"""
Router definitions for VisionF1 endpoints.
"""

import logging
from fastapi import APIRouter
from visionf1.controller.controller import get_driver_standings_controller, get_team_standings_controller, get_drivers_controller, get_upcoming_gp_controller, get_events_controller
from visionf1.models.models import DriverStandingsResponse, TeamStandingsResponse, DriversResponse, UpcomingGPResponse, EventsResponse

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

@router.get("/team-standings", response_model=TeamStandingsResponse, status_code=200, tags=["GET /team-standings"])
async def get_team_standings_endpoint():
    """
    Routes GET /team-standings endpoint.
    """
    logger.info("GET /team-standings endpoint called.")
    return get_team_standings_controller()

@router.get("/drivers", response_model=DriversResponse, status_code=200, tags=["GET /drivers"])
async def get_drivers_endpoint():
    """
    Routes GET /drivers endpoint.
    """
    logger.info("GET /drivers endpoint called.")
    return get_drivers_controller()

@router.get("/upcoming-gp", response_model=UpcomingGPResponse, status_code=200, tags=["GET /upcoming-gp"])
async def get_upcoming_gp_endpoint():
    """
    Routes GET /upcoming-gp endpoint.
    """
    logger.info("GET /upcoming-gp endpoint called.")
    return get_upcoming_gp_controller()

@router.get("/events", response_model=EventsResponse, status_code=200, tags=["GET /events"])
async def get_events_endpoint(season: int = None):
    """
    GET /events?season=YYYY
    If season is provided, returns events for that year; otherwise returns all events.
    """
    logger.info(f"GET /events endpoint called. Season={season}")
    return get_events_controller(season=season)
