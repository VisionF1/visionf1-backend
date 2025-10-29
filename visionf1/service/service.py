"""
Service layer: Data managing logic.
"""

import logging
from visionf1.database.database import get_driver_standings, get_team_standings, get_drivers, get_upcoming_gp, get_events, get_summary_events, get_seasons, get_race_pace
from visionf1.models.models import DriverStanding, TeamStanding, Driver, UpcomingGP, Event, EventSummary, RacePace
from typing import List

logger = logging.getLogger(__name__)


def obtain_driver_standings() -> List[DriverStanding]:
    """
    Retrieves stored driver standings.
    """
    logger.debug("Obtaining driver standings.")
    return get_driver_standings()

def obtain_team_standings() -> List[TeamStanding]:
    """
    Retrieves stored team standings.
    """
    logger.debug("Obtaining team standings.")
    return get_team_standings()

def obtain_drivers() -> List[Driver]:
    """
    Retrieves stored drivers.
    """
    logger.debug("Obtaining drivers.")
    return get_drivers()

def obtain_upcoming_gp() -> List[UpcomingGP]:
    """
    Retrieves stored upcoming GP entries.
    """
    logger.debug("Obtaining upcoming GP entries.")
    return get_upcoming_gp()

def obtain_events(season: int = None) -> List[Event]:
    """
    Retrieves stored events (optionally filtered by season).
    """
    logger.debug(f"Obtaining events for season={season}.")
    return get_events(season=season)

def obtain_summary_events(season: int = None) -> List[EventSummary]:
    """
    Retrieves stored summary events (optionally filtered by season).
    """
    logger.debug(f"Obtaining summary events for season={season}.")
    return get_summary_events(season=season)

def obtain_seasons() -> List[int]:
    """
    Retrieves available seasons (years) from DB.
    """
    return get_seasons()

def obtain_race_pace(season: int = None, round: int = None, event_id: str = None) -> List[RacePace]:
    """
    Retrieves stored race pace data (optionally filtered by season, round, or event_id).
    """
    logger.debug(f"Obtaining race pace season={season} round={round} event_id={event_id}")
    return get_race_pace(season=season, round=round, event_id=event_id)
