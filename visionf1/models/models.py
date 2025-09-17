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
    driver_code: str
    nationality: str
    nationality_code: str
    team: str
    team_code: str
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
