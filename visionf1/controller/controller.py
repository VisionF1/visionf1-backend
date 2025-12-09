"""
Controller handles request validation, response formatting, and interaction with services.
"""

import logging
import pandas as pd
from visionf1.service.service import obtain_driver_standings, obtain_team_standings, obtain_drivers, obtain_upcoming_gp, obtain_events, obtain_summary_events, obtain_seasons, obtain_race_pace, obtain_clean_air_race_pace, obtain_lap_time_distributions
from visionf1.models.models import DriverStandingsResponse, TeamStandingsResponse, DriversResponse, UpcomingGPResponse, EventsResponse, EventsSummaryResponse, SeasonsResponse, RacePaceResponse, CleanAirRacePaceResponse, LapTimeDistributionResponse, RacePredictionInput, RacePredictionOutput, RacePredictionResponse, StrategyRequest, StrategyPrediction, StrategyPredictionResponse, Stint, Window
from visionf1.ml.race_predictor import CachedRacePredictor
from visionf1.ml.strategy_predictor import CachedStrategyPredictor

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

def get_clean_air_race_pace_controller(season: int = None, round: int = None, event_id: str = None) -> CleanAirRacePaceResponse:
    """
    Retrieves clean air race pace data (optionally filtered by season, round, or event_id).
    """
    rp = obtain_clean_air_race_pace(season=season, round=round, event_id=event_id)
    bad = _find_bad_entries(rp)
    if bad:
        for idx, key, val, doc in bad:
            logger.error(f"Bad value in clean_air_race_pace result idx={idx} key={key} val={val} doc_sample={repr(doc)[:1000]}")
    logger.info(f"Retrieving clean air race pace for season={season} round={round} event_id={event_id}")
    clean_air_race_pace = obtain_clean_air_race_pace(season=season, round=round, event_id=event_id)
    return CleanAirRacePaceResponse(data=clean_air_race_pace)

def get_lap_time_distributions_controller(season: int = None, round: int = None, event_id: str = None) -> LapTimeDistributionResponse:
    """
    Retrieves lap time distribution data (optionally filtered by season, round, or event_id).
    """
    ltd = obtain_lap_time_distributions(season=season, round=round, event_id=event_id)
    bad = _find_bad_entries(ltd)
    if bad:
        for idx, key, val, doc in bad:
            logger.error(f"Bad value in lap_time_distributions result idx={idx} key={key} val={val} doc_sample={repr(doc)[:1000]}")
    logger.info(f"Retrieving lap time distributions for season={season} round={round} event_id={event_id}")
    lap_time_distributions = obtain_lap_time_distributions(season=season, round=round, event_id=event_id)
    return LapTimeDistributionResponse(data=lap_time_distributions)

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

def predict_strategy_controller(req: StrategyRequest) -> StrategyPredictionResponse:
    """
    Predicts race strategy for a specific race.
    
    Args:
        req: Strategy request containing circuit and other parameters
    
    Returns:
        StrategyPredictionResponse with sorted predictions
    """
    logger.info(f"Predicting strategy for {req.circuit}")
    
    # Get predictor instance and predict
    predictor = CachedStrategyPredictor()

    candidates = predictor.predict(
        circuit=req.circuit,
        track_temp=req.track_temp,
        air_temp=req.air_temp,
        compounds=req.compounds,
        max_stops=req.max_stops,
        fia_rule=req.fia_rule,
        top_k=req.top_k
    )
    
    response = []
    for c in candidates:
        stints = [
            Stint(compound=s[0], start_lap=s[1], end_lap=s[2]) 
            for s in c.stints
        ]
        windows = [
            Window(p25=w[0], p50=w[1], p75=w[2])
            for w in c.windows
        ]
        response.append(StrategyPrediction(
            template=c.template,
            stints=stints,
            windows=windows,
            expected_race_time=c.expected_total_race_time,
            probability=c.prob
        ))

    final_response = StrategyPredictionResponse(predictions=response)

    logger.info(f"Strategy predicted for {req.circuit}")    
    return final_response
