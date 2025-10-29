"""
Controller handles request validation, response formatting, and interaction with services.
"""

import logging
from visionf1.service.service import obtain_driver_standings, obtain_team_standings, obtain_drivers, obtain_upcoming_gp, obtain_events, obtain_summary_events, obtain_seasons
from visionf1.models.models import DriverStandingsResponse, TeamStandingsResponse, DriversResponse, UpcomingGPResponse, EventsResponse, EventsSummaryResponse, SeasonsResponse

logger = logging.getLogger(__name__)


def get_driver_standings_controller() -> DriverStandingsResponse:
    """
    Retrieves driver standings.
    """
    logger.info("Retrieving driver standings...")
    driver_standings = obtain_driver_standings()
    logger.debug(f"Driver standings retrieved: {driver_standings}")
    return DriverStandingsResponse(data=driver_standings)

def get_team_standings_controller() -> TeamStandingsResponse:
    """
    Retrieves team standings.
    """
    logger.info("Retrieving team standings...")
    team_standings = obtain_team_standings()
    logger.debug(f"Team standings retrieved: {team_standings}")
    return TeamStandingsResponse(data=team_standings)

def get_drivers_controller() -> DriversResponse:
    """
    Retrieves drivers.
    """
    logger.info("Retrieving drivers...")
    drivers = obtain_drivers()
    logger.debug(f"Drivers retrieved: {drivers}")
    return DriversResponse(data=drivers)

def get_upcoming_gp_controller() -> UpcomingGPResponse:
    """
    Retrieves upcoming GP.
    """
    logger.info("Retrieving upcoming GP entries...")
    upcoming = obtain_upcoming_gp()
    logger.debug(f"Upcoming GP retrieved: {upcoming}")
    return UpcomingGPResponse(data=upcoming)

def get_events_controller(season: int = None) -> EventsResponse:
    """
    Retrieves events (optionally filtered by season).
    """
    logger.info(f"Retrieving events for season={season}...")
    events = obtain_events(season=season)
    logger.debug(f"Events retrieved: {events}")
    return EventsResponse(data=events)

def get_summary_events_controller(season: int = None) -> EventsSummaryResponse:
    """
    Retrieves summary events (optionally filtered by season).
    """
    logger.info(f"Retrieving summary events for season={season}...")
    events = obtain_summary_events(season=season)
    logger.debug(f"Summary events retrieved: {events}")
    return EventsSummaryResponse(data=events)

def get_seasons_controller() -> SeasonsResponse:
    """
    Controller returning available seasons.
    """
    logger.info("Retrieving distinct seasons")
    seasons = obtain_seasons()
    return SeasonsResponse(data=seasons)
