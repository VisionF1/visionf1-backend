"""
Controller handles request validation, response formatting, and interaction with services.
"""

import logging
import pandas as pd
from visionf1.service.service import obtain_driver_standings, obtain_team_standings, obtain_drivers, obtain_upcoming_gp, obtain_events, obtain_summary_events, obtain_seasons, obtain_race_pace
from visionf1.models.models import DriverStandingsResponse, TeamStandingsResponse, DriversResponse, UpcomingGPResponse, EventsResponse, EventsSummaryResponse, SeasonsResponse, RacePaceResponse, RacePredictionInput, RacePredictionOutput, RacePredictionResponse
from visionf1.ml.race_predictor import CachedRacePredictor

logger = logging.getLogger(__name__)


def get_driver_standings_controller() -> DriverStandingsResponse:
    """
    Retrieves driver standings.
    """
    logger.info("Retrieving driver standings...")
    driver_standings = obtain_driver_standings()
    logger.debug(f"Driver standings retrieved: {driver_standings}")
    return DriverStandingsResponse(data=driver_standings)

def get_team_standings_controller() -> TeamStandingsResponse:
    """
    Retrieves team standings.
    """
    logger.info("Retrieving team standings...")
    team_standings = obtain_team_standings()
    logger.debug(f"Team standings retrieved: {team_standings}")
    return TeamStandingsResponse(data=team_standings)

def get_drivers_controller() -> DriversResponse:
    """
    Retrieves drivers.
    """
    logger.info("Retrieving drivers...")
    drivers = obtain_drivers()
    logger.debug(f"Drivers retrieved: {drivers}")
    return DriversResponse(data=drivers)

def get_upcoming_gp_controller() -> UpcomingGPResponse:
    """
    Retrieves upcoming GP.
    """
    logger.info("Retrieving upcoming GP entries...")
    upcoming = obtain_upcoming_gp()
    logger.debug(f"Upcoming GP retrieved: {upcoming}")
    return UpcomingGPResponse(data=upcoming)

def get_events_controller(season: int = None) -> EventsResponse:
    """
    Retrieves events (optionally filtered by season).
    """
    logger.info(f"Retrieving events for season={season}...")
    events = obtain_events(season=season)
    logger.debug(f"Events retrieved: {events}")
    return EventsResponse(data=events)

def get_summary_events_controller(season: int = None) -> EventsSummaryResponse:
    """
    Retrieves summary events (optionally filtered by season).
    """
    logger.info(f"Retrieving summary events for season={season}...")
    events = obtain_summary_events(season=season)
    logger.debug(f"Summary events retrieved: {events}")
    return EventsSummaryResponse(data=events)

def get_seasons_controller() -> SeasonsResponse:
    """
    Retrieves available seasons.
    """
    logger.info("Retrieving distinct seasons")
    seasons = obtain_seasons()
    return SeasonsResponse(data=seasons)

def _find_bad_entries(entries):
    import math
    bad = []
    for i, e in enumerate(entries):
        # e puede ser Pydantic model o dict
        d = e.dict() if hasattr(e, "dict") else dict(e)
        for k, v in d.items():
            # detectar NaN en floats y numpy scalars convertibles
            try:
                if isinstance(v, float) and math.isnan(v):
                    bad.append((i, k, v, d))
            except Exception:
                pass
    return bad

def get_race_pace_controller(season: int = None, round: int = None, event_id: str = None) -> RacePaceResponse:
    """
    Retrieves race pace data (optionally filtered by season, round, or event_id).
    """
    rp = obtain_race_pace(season=season, round=round, event_id=event_id)
    bad = _find_bad_entries(rp)
    if bad:
        for idx, key, val, doc in bad:
            logger.error(f"Bad value in race_pace result idx={idx} key={key} val={val} doc_sample={repr(doc)[:1000]}")
    logger.info(f"Retrieving race pace for season={season} round={round} event_id={event_id}")
    race_pace = obtain_race_pace(season=season, round=round, event_id=event_id)
    return RacePaceResponse(data=race_pace)

def predict_race_controller(drivers: list[RacePredictionInput]) -> RacePredictionResponse:
    """
    Predicts race positions for a list of drivers.
    
    Args:
        drivers: List of driver inputs for the same race
    
    Returns:
        RacePredictionResponse with sorted predictions
    """
    logger.info(f"Predicting race for {len(drivers)} drivers...")
    
    # Convert Pydantic models to DataFrame
    df_raw = pd.DataFrame([d.model_dump() for d in drivers])
    
    # Get predictor instance and predict
    predictor = CachedRacePredictor()
    predictions = predictor.predict(df_raw)
    
    # Create output with rankings
    results = []
    for i, pred in enumerate(predictions):
        results.append({
            "driver": drivers[i].driver,
            "team": drivers[i].team,
            "predicted_position": float(pred),
            "rank": 0  # Will be assigned after sorting
        })
    
    # Sort by predicted position and assign ranks
    results.sort(key=lambda x: x["predicted_position"])
    for rank, result in enumerate(results, start=1):
        result["rank"] = rank
    
    response = RacePredictionResponse(
        race_name=drivers[0].race_name,
        year=drivers[0].year,
        predictions=[RacePredictionOutput(**r) for r in results]
    )
    
    logger.info(f"Predictions completed. Winner: {results[0]['driver']}")
    return response
