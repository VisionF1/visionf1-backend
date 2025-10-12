"""
Service layer: Data managing logic.
"""

import logging
from visionf1.database.database import get_driver_standings, get_team_standings, get_drivers, get_upcoming_gp
from visionf1.models.models import DriverStanding
from typing import List

logger = logging.getLogger(__name__)


def obtain_driver_standings() -> List[DriverStanding]:
    """
    Retrieves stored driver standings.
    """
    logger.debug("Obtaining driver standings.")
    return get_driver_standings()

def obtain_team_standings() -> List[DriverStanding]:
    """
    Retrieves stored team standings.
    """
    logger.debug("Obtaining team standings.")
    return get_team_standings()

def obtain_drivers() -> List[DriverStanding]:
    """
    Retrieves stored drivers.
    """
    logger.debug("Obtaining drivers.")
    return get_drivers()

def obtain_upcoming_gp() -> List[DriverStanding]:
    """
    Retrieves stored upcoming GP entries.
    """
    logger.debug("Obtaining upcoming GP entries.")
    return get_upcoming_gp()
