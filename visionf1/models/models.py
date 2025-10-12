"""
Data models and schemas for the API.
"""

from pydantic import BaseModel
from typing import List
from datetime import datetime


class DriverStanding(BaseModel):
    """
    Model representing a driver's standing.
    """
    position: int
    driver: str
    driverCode: str
    nationality: str
    nationalityCode: str
    team: str
    teamCode: str
    points: int

class DriverStandingsResponse(BaseModel):
    """
    Schema for driver standings response.
    """
    data: List[DriverStanding]

class TeamStanding(BaseModel):
    """
    Model representing a team's standing.
    """
    position: int
    team: str
    teamCode: str
    nationality: str
    nationalityCode: str
    points: int

class TeamStandingsResponse(BaseModel):
    """
    Schema for team standings response.
    """
    data: List[TeamStanding]

class Driver(BaseModel):
    """
    Model representing a driver.
    """
    firstName: str = None
    lastName: str = None
    driverCode: str
    nationalityCode2: str = None
    nationalityCode3: str = None
    team: str = None
    teamCode: str = None

class DriversResponse(BaseModel):
    """
    Schema for drivers response.
    """
    data: List[Driver]

class UpcomingGP(BaseModel):
    """
    Model representing an upcoming Grand Prix entry.
    """
    id: str
    season: int
    round: int
    name: str
    circuitId: str = None
    circuit: str = None
    countryCode: str = None
    country: str = None
    locality: str = None
    startDate: datetime = None
    endDate: datetime = None

class UpcomingGPResponse(BaseModel):
    """
    Schema for upcoming GP response.
    """
    data: List[UpcomingGP]

class ErrorResponse(BaseModel):
    """
    Error response model following RFC 7807.
    """
    type: str
    title: str
    status: int
    detail: str
    instance: str
