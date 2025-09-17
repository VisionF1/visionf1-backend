"""
Service layer: Data managing logic.
"""

import logging
from visionf1.database.database import get_driver_standings
from visionf1.models.models import DriverStanding
from typing import List

logger = logging.getLogger(__name__)


def obtain_driver_standings() -> List[DriverStanding]:
    """
    Retrieves stored driver standings.
    """
    logger.debug("Obtaining driver standings.")
    return get_driver_standings()
