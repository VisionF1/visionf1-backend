"""
Data models and schemas for the API.
"""

from pydantic import BaseModel, Field
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
    teamColor: str

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
    country_code: str
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

class RacePace(BaseModel):
    """
    Model representing a race pace entry.
    """
    race_pace_id: str
    season: int
    round: int
    event: str
    driver: str
    driver_first_name: str
    driver_last_name: str
    driver_position: int
    driver_color: str
    team: str
    team_name: str
    team_color: str
    avg_laptime: float
    std_laptime: float | None
    race_pace_position: int

class RacePaceResponse(BaseModel):
    """
    Schema for race pace response.
    """
    data: List[RacePace]

class RacePredictionInput(BaseModel):
    """
    Input for race prediction endpoint.
    """
    driver: str = Field(..., example="VER", description="Driver code (e.g., VER, HAM)")
    team: str = Field(..., example="Red Bull Racing", description="Team name")
    race_name: str = Field(..., example="Singapore Grand Prix", description="Race name")
    year: int = Field(2025, ge=2020, le=2030, description="Season year")
    session_air_temp: float = Field(26.0, ge=-10, le=50, description="Air temperature in °C")
    session_track_temp: float = Field(35.0, ge=-10, le=70, description="Track temperature in °C")
    session_humidity: float = Field(60.0, ge=0, le=100, description="Humidity percentage")
    session_rainfall: float = Field(0.0, ge=0, le=1, description="Rainfall (0=dry, 1=wet)")
    circuit_type: str = Field("street", pattern="^(street|permanent)$", description="Circuit type")

class RacePredictionOutput(BaseModel):
    """
    Single driver prediction output.
    """
    driver: str
    team: str
    predicted_position: float
    rank: int

class RacePredictionResponse(BaseModel):
    """
    Response with predictions for all drivers in the race.
    """
    race_name: str
    year: int
    predictions: List[RacePredictionOutput]

class ErrorResponse(BaseModel):
    """
    Error response model following RFC 7807.
    """
    type: str
    title: str
    status: int
    detail: str
    instance: str
