"""
Data models and schemas for the API.
"""

from pydantic import BaseModel
from typing import List


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

class ErrorResponse(BaseModel):
    """
    Error response model following RFC 7807.
    """
    type: str
    title: str
    status: int
    detail: str
    instance: str
