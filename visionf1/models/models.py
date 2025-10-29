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
    driverId: str
    driverNumber: int
    driverCode: str
    driverUrl: str
    firstName: str
    lastName: str
    dateOfBirth: datetime
    driverNationality: str
    nationalityCode2: str
    nationalityCode3: str
    team: str
    teamCode: str

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
    circuitId: str
    circuit: str
    countryCode: str
    country: str
    locality: str
    startDate: datetime
    endDate: datetime

class UpcomingGPResponse(BaseModel):
    """
    Schema for upcoming GP response.
    """
    data: List[UpcomingGP]

class Event(BaseModel):
    """
    Model representing an event.
    """
    event_id: str
    season: int
    round: int
    event_name: str
    country: str
    location: str
    event_date: datetime
    event_format: str
    event_status: str
    circuit_id: str
    circuit_name: str
    n_drivers: int
    driver_codes: List[str]
    driver_names: List[str]
    n_teams: int
    team_codes: List[str]
    team_names: List[str]
    team_colors: List[str]
    winner: str | None
    pole: str | None

class EventsResponse(BaseModel):
    """
    Schema for event response.
    """
    data: List[Event]

class EventSummary(BaseModel):
    """
    Model representing a summarized event.
    """
    event_id: str
    season: int
    round: int
    event_name: str
    event_date: datetime
    event_status: str

class EventsSummaryResponse(BaseModel):
    """
    Schema for summarized event response.
    """
    data: List[EventSummary]

class SeasonsResponse(BaseModel):
    """
    Schema for seasons response.
    """
    data: List[int]

class ErrorResponse(BaseModel):
    """
    Error response model following RFC 7807.
    """
    type: str
    title: str
    status: int
    detail: str
    instance: str
