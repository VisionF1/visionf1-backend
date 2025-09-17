"""
In-memory database simulation for driver standings.
"""

import logging
from visionf1.models.models import DriverStanding
from typing import List

logger = logging.getLogger(__name__)


# Simulated in-memory DB
database: List[DriverStanding] = [
  DriverStanding(position=1, driver="Oscar Piastri", driver_code="PIA", nationality="AUS", nationality_code="au", team="McLaren", team_code="MCL", points=324),
  DriverStanding(position=2, driver="Lando Norris", driver_code="NOR", nationality="GBR", nationality_code="gb", team="McLaren", team_code="MCL", points=293),
  DriverStanding(position=3, driver="Max Verstappen", driver_code="VER", nationality="NED", nationality_code="nl", team="Red Bull Racing", team_code="RB", points=230),
  DriverStanding(position=4, driver="George Russell", driver_code="RUS", nationality="GBR", nationality_code="gb", team="Mercedes", team_code="MER", points=194),
  DriverStanding(position=5, driver="Charles Leclerc", driver_code="LEC", nationality="MON", nationality_code="mc", team="Ferrari", team_code="FER", points=163),
  DriverStanding(position=6, driver="Lewis Hamilton", driver_code="HAM", nationality="GBR", nationality_code="gb", team="Ferrari", team_code="FER", points=117),
  DriverStanding(position=7, driver="Alexander Albon", driver_code="ALB", nationality="THA", nationality_code="th", team="Williams", team_code="WIL", points=70),
  DriverStanding(position=8, driver="Kimi Antonelli", driver_code="ANT", nationality="ITA", nationality_code="it", team="Mercedes", team_code="MER", points=66),
  DriverStanding(position=9, driver="Isack Hadjar", driver_code="HAD", nationality="FRA", nationality_code="fr", team="Racing Bulls", team_code="RBU", points=38),
  DriverStanding(position=10, driver="Nico Hulkenberg", driver_code="HUL", nationality="GER", nationality_code="de", team="Kick Sauber", team_code="SAU", points=37),
  DriverStanding(position=11, driver="Lance Stroll", driver_code="STR", nationality="CAN", nationality_code="ca", team="Aston Martin", team_code="AM", points=32),
  DriverStanding(position=12, driver="Fernando Alonso", driver_code="ALO", nationality="ESP", nationality_code="es", team="Aston Martin", team_code="AM", points=30),
  DriverStanding(position=13, driver="Esteban Ocon", driver_code="OCO", nationality="FRA", nationality_code="fr", team="Haas", team_code="HAA", points=28),
  DriverStanding(position=14, driver="Pierre Gasly", driver_code="GAS", nationality="FRA", nationality_code="fr", team="Alpine", team_code="ALP", points=20),
  DriverStanding(position=15, driver="Liam Lawson", driver_code="LAW", nationality="NZL", nationality_code="nz", team="Racing Bulls", team_code="RBU", points=20),
  DriverStanding(position=16, driver="Gabriel Bortoleto", driver_code="BOR", nationality="BRA", nationality_code="br", team="Kick Sauber", team_code="SAU", points=18),
  DriverStanding(position=17, driver="Oliver Bearman", driver_code="BEA", nationality="GBR", nationality_code="gb", team="Haas", team_code="HAA", points=16),
  DriverStanding(position=18, driver="Carlos Sainz", driver_code="SAI", nationality="ESP", nationality_code="es", team="Williams", team_code="WIL", points=16),
  DriverStanding(position=19, driver="Yuki Tsunoda", driver_code="TSU", nationality="JPN", nationality_code="jp", team="Red Bull Racing", team_code="RB", points=12),
  DriverStanding(position=20, driver="Franco Colapinto", driver_code="COL", nationality="ARG", nationality_code="ar", team="Alpine", team_code="ALP", points=0),
  DriverStanding(position=21, driver="Jack Doohan", driver_code="DOO", nationality="AUS", nationality_code="au", team="Alpine", team_code="ALP", points=0),
]

def get_driver_standings() -> List[DriverStanding]:
    """
    Retrieves driver standings.
    """
    logger.debug("Retrieving driver standings from database.")
    return database
