"""
In-memory database simulation for driver standings.
"""

import logging
from visionf1.models.models import DriverStanding
from typing import List

logger = logging.getLogger(__name__)


# Simulated in-memory DB
database: List[DriverStanding] = [
  DriverStanding(position=1, driver="Oscar Piastri", driverCode="PIA", nationality="AUS", nationalityCode="au", team="McLaren", teamCode="MCL", points=324),
  DriverStanding(position=2, driver="Lando Norris", driverCode="NOR", nationality="GBR", nationalityCode="gb", team="McLaren", teamCode="MCL", points=293),
  DriverStanding(position=3, driver="Max Verstappen", driverCode="VER", nationality="NED", nationalityCode="nl", team="Red Bull Racing", teamCode="RB", points=230),
  DriverStanding(position=4, driver="George Russell", driverCode="RUS", nationality="GBR", nationalityCode="gb", team="Mercedes", teamCode="MER", points=194),
  DriverStanding(position=5, driver="Charles Leclerc", driverCode="LEC", nationality="MON", nationalityCode="mc", team="Ferrari", teamCode="FER", points=163),
  DriverStanding(position=6, driver="Lewis Hamilton", driverCode="HAM", nationality="GBR", nationalityCode="gb", team="Ferrari", teamCode="FER", points=117),
  DriverStanding(position=7, driver="Alexander Albon", driverCode="ALB", nationality="THA", nationalityCode="th", team="Williams", teamCode="WIL", points=70),
  DriverStanding(position=8, driver="Kimi Antonelli", driverCode="ANT", nationality="ITA", nationalityCode="it", team="Mercedes", teamCode="MER", points=66),
  DriverStanding(position=9, driver="Isack Hadjar", driverCode="HAD", nationality="FRA", nationalityCode="fr", team="Racing Bulls", teamCode="RBU", points=38),
  DriverStanding(position=10, driver="Nico Hulkenberg", driverCode="HUL", nationality="GER", nationalityCode="de", team="Kick Sauber", teamCode="SAU", points=37),
  DriverStanding(position=11, driver="Lance Stroll", driverCode="STR", nationality="CAN", nationalityCode="ca", team="Aston Martin", teamCode="AM", points=32),
  DriverStanding(position=12, driver="Fernando Alonso", driverCode="ALO", nationality="ESP", nationalityCode="es", team="Aston Martin", teamCode="AM", points=30),
  DriverStanding(position=13, driver="Esteban Ocon", driverCode="OCO", nationality="FRA", nationalityCode="fr", team="Haas", teamCode="HAA", points=28),
  DriverStanding(position=14, driver="Pierre Gasly", driverCode="GAS", nationality="FRA", nationalityCode="fr", team="Alpine", teamCode="ALP", points=20),
  DriverStanding(position=15, driver="Liam Lawson", driverCode="LAW", nationality="NZL", nationalityCode="nz", team="Racing Bulls", teamCode="RBU", points=20),
  DriverStanding(position=16, driver="Gabriel Bortoleto", driverCode="BOR", nationality="BRA", nationalityCode="br", team="Kick Sauber", teamCode="SAU", points=18),
  DriverStanding(position=17, driver="Oliver Bearman", driverCode="BEA", nationality="GBR", nationalityCode="gb", team="Haas", teamCode="HAA", points=16),
  DriverStanding(position=18, driver="Carlos Sainz", driverCode="SAI", nationality="ESP", nationalityCode="es", team="Williams", teamCode="WIL", points=16),
  DriverStanding(position=19, driver="Yuki Tsunoda", driverCode="TSU", nationality="JPN", nationalityCode="jp", team="Red Bull Racing", teamCode="RB", points=12),
  DriverStanding(position=20, driver="Franco Colapinto", driverCode="COL", nationality="ARG", nationalityCode="ar", team="Alpine", teamCode="ALP", points=0),
  DriverStanding(position=21, driver="Jack Doohan", driverCode="DOO", nationality="AUS", nationalityCode="au", team="Alpine", teamCode="ALP", points=0),
]

def get_driver_standings() -> List[DriverStanding]:
    """
    Retrieves driver standings.
    """
    logger.debug("Retrieving driver standings from database.")
    return database
