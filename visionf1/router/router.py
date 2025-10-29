"""
Router definitions for VisionF1 endpoints.
"""

import logging
from fastapi import APIRouter
from visionf1.controller.controller import get_driver_standings_controller, get_team_standings_controller, get_drivers_controller, get_upcoming_gp_controller, get_events_controller, get_summary_events_controller, get_seasons_controller, get_race_pace_controller
from visionf1.models.models import DriverStandingsResponse, TeamStandingsResponse, DriversResponse, UpcomingGPResponse, EventsResponse, EventsSummaryResponse, SeasonsResponse, RacePaceResponse

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
    Routes GET /events?season=YYYY endpoint.
    If season is provided, returns events for that year; otherwise returns all events.
    """
    logger.info(f"GET /events endpoint called. Season={season}")
    return get_events_controller(season=season)

@router.get("/summary-events", response_model=EventsSummaryResponse, status_code=200, tags=["GET /summary-events"])
async def get_summary_events_endpoint(season: int = None):
    """
    Routes GET /summary-events?season=YYYY endpoint.
    If season is provided, returns summary events for that year; otherwise returns all summary events.
    """
    logger.info(f"GET /summary-events endpoint called. Season={season}")
    return get_summary_events_controller(season=season)

@router.get("/seasons", response_model=SeasonsResponse, status_code=200, tags=["GET /seasons"])
async def get_seasons_endpoint():
    """
    Routes GET /seasons endpoint.
    """
    logger.info("GET /seasons called")
    return get_seasons_controller()

@router.get("/race-pace", response_model=RacePaceResponse, status_code=200, tags=["GET /race-pace"])
async def get_race_pace_endpoint(season: int = None, round: int = None, event_id: str = None):
    """
    Routes GET /race-pace?season=YYYY&round=N endpoint
            or
           GET /race-pace?event_id=SEASON_ROUND_EventName endpoint.
    Returns race pace entries for all drivers in the GP.
    """
    logger.info(f"GET /race-pace called season={season} round={round} event_id={event_id}")
    return get_race_pace_controller(season=season, round=round, event_id=event_id)
