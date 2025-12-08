"""
MongoDB database connection and operations for driver standings.
"""

import logging
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from visionf1.models.models import DriverStanding, TeamStanding, Driver, UpcomingGP, Event, EventSummary, RacePace, CleanAirRacePace
from typing import List

load_dotenv()

logger = logging.getLogger(__name__)

# MongoDB connection
MONGODB_URL = os.getenv('MONGODB_URL')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'VisionF1')

if not MONGODB_URL:
    raise ValueError("MONGODB_URL environment variable is required")

client = MongoClient(MONGODB_URL)
database = client[DATABASE_NAME]
driver_standings_collection = database.driver_standings
team_standings_collection = database.team_standings
drivers_collection = database.drivers
upcoming_gp_collection = database.upcoming_gp
events_collection = database.events
race_pace_collection = database.race_pace
clean_air_race_pace_collection = database.clean_air_race_pace

def get_driver_standings() -> List[DriverStanding]:
    """
    Retrieves driver standings from MongoDB.
    """
    logger.debug("Retrieving driver standings from MongoDB.")
    
    try:
        # Get all documents from the collection, sorted by position
        cursor = driver_standings_collection.find().sort("position", 1)
        
        driver_standings = []
        for doc in cursor:
            # Convert the MongoDB document to DriverStanding
            # Exclude the _id field that MongoDB automatically adds
            doc.pop('_id', None)
            driver_standing = DriverStanding(**doc)
            driver_standings.append(driver_standing)
        
        logger.debug(f"Retrieved {len(driver_standings)} driver standings from MongoDB.")
        return driver_standings
        
    except Exception as e:
        logger.error(f"Error retrieving driver standings from MongoDB: {e}")
        raise e

def get_team_standings() -> List[TeamStanding]:
    """
    Retrieves team standings from MongoDB.
    """
    logger.debug("Retrieving team standings from MongoDB.")

    try:
        # Get all documents from the collection, sorted by position
        cursor = team_standings_collection.find().sort("position", 1)

        team_standings = []
        for doc in cursor:
            # Convert the MongoDB document to TeamStanding
            # Exclude the _id field that MongoDB automatically adds
            doc.pop('_id', None)
            team_standings.append(TeamStanding(**doc))
        logger.debug(f"Retrieved {len(team_standings)} team standings from MongoDB.")
        return team_standings
    except Exception as e:
        logger.error(f"Error retrieving team standings from MongoDB: {e}")
        raise e

def get_drivers() -> List[Driver]:
    """
    Retrieves drivers from MongoDB.
    """
    logger.debug("Retrieving drivers from MongoDB.")

    try:
        # Get all documents from the collection, sorted by team and lastName
        cursor = drivers_collection.find().sort([("team", 1), ("lastName", 1)])
        drivers = []
        for doc in cursor:
            # Convert the MongoDB document to Driver
            # Exclude the _id field that MongoDB automatically adds
            doc.pop('_id', None)
            drivers.append(Driver(**doc))
        logger.debug(f"Retrieved {len(drivers)} drivers from MongoDB.")
        return drivers
    except Exception as e:
        logger.error(f"Error retrieving drivers from MongoDB: {e}")
        raise e

def get_upcoming_gp() -> UpcomingGP:
    """
    Retrieves upcoming GP entries from MongoDB.
    """
    logger.debug("Retrieving upcoming GP from MongoDB.")

    try:
        # Get all documents from the collection, sorted by startDate
        cursor = upcoming_gp_collection.find().sort("startDate", 1)
        upcoming_gp = []
        for doc in cursor:
            # Convert the MongoDB document to UpcomingGP
            # Exclude the _id field that MongoDB automatically adds
            doc.pop('_id', None)
            upcoming_gp.append(UpcomingGP(**doc))
        logger.debug(f"Retrieved {len(upcoming_gp)} upcoming GP entries from MongoDB.")
        return upcoming_gp
    except Exception as e:
        logger.error(f"Error retrieving upcoming GP from MongoDB: {e}")
        raise e

def get_events(season: int = None) -> List[Event]:
    """
    Retrieves events from MongoDB.
    If season is provided, filters by season.
    """
    logger.debug("Retrieving events from MongoDB.")
    try:
        query = {}
        if season is not None:
            query["season"] = int(season)

        cursor = events_collection.find(query).sort([("season", 1), ("round", 1)])
        events = []
        for doc in cursor:
            doc.pop("_id", None)
            # Convert the MongoDB document to Event
            # Exclude the _id field that MongoDB automatically adds
            events.append(Event(**doc))
        logger.debug(f"Retrieved {len(events)} events from MongoDB.")
        return events
    except Exception as e:
        logger.error(f"Error retrieving events from MongoDB: {e}")
        raise e
    
def get_summary_events(season: int = None) -> List[EventSummary]:
    """
    Retrieves lightweight events (projection) from MongoDB to reduce payload.
    """
    logger.debug(f"Retrieving summary events for season={season} from MongoDB.")
    try:
        query = {}
        if season is not None:
            query["season"] = int(season)

        projection = {
                "_id": False,
                "event_id": True,
                "season": True,
                "round": True,
                "event_name": True,
                "event_date": True,
                "event_status": True,
            }

        cursor = events_collection.find(query, projection).sort([("season", 1), ("round", 1)])
        summary_events = []
        for doc in cursor:
            doc.pop("_id", None)
            # Convert the MongoDB document to Event
            # Exclude the _id field that MongoDB automatically adds
            summary_events.append(EventSummary(**doc))
        logger.debug(f"Retrieved {len(summary_events)} summary events from MongoDB.")
        return summary_events
    except Exception as e:
        logger.error(f"Error retrieving summary events from MongoDB: {e}")
        raise e

def get_seasons() -> List[int]:
    """
    Return sorted list of distinct seasons found in events collection from MongoDB.
    """
    logger.debug("Retrieving seasons from MongoDB.")
    try:
        seasons = events_collection.distinct("season")
        logger.debug(f"Retrieved {len(seasons)} seasons from MongoDB.")
        return sorted([int(s) for s in seasons if s is not None])
    except Exception as e:
        logger.error(f"Error fetching seasons: {e}")
        raise e
    
def get_race_pace(season: int = None, round: int = None, event_id: str = None) -> List[RacePace]:
    """
    Retrieve race pace documents filtered by season+round or event_id.
    """
    logger.debug(f"Retrieving race pace season={season} round={round} event_id={event_id}")
    try:
        query = {}
        if event_id:
            query["race_pace_id"] = event_id
        else:
            if season is not None:
                query["season"] = int(season)
            if round is not None:
                query["round"] = int(round)

        cursor = race_pace_collection.find(query, projection={"_id": False}).sort([("season", 1), ("round", 1), ("driver", 1)])
        results = []
        for doc in cursor:
            doc.pop("_id", None)
            # Convert the MongoDB document to Event
            # Exclude the _id field that MongoDB automatically adds
            results.append(RacePace(**doc))
        logger.debug(f"Retrieved {len(results)} race pace records.")
        return results
    except Exception as e:
        logger.error(f"Error retrieving race pace from MongoDB: {e}")
        raise e

def get_clean_air_race_pace(season: int = None, round: int = None, event_id: str = None) -> List[CleanAirRacePace]:
    """
    Retrieve clean air race pace documents filtered by season+round or event_id.
    """
    logger.debug(f"Retrieving clean air race pace season={season} round={round} event_id={event_id}")
    try:
        query = {}
        if event_id:
            query["clean_air_race_pace_id"] = event_id
        else:
            if season is not None:
                query["season"] = int(season)
            if round is not None:
                query["round"] = int(round)

        cursor = clean_air_race_pace_collection.find(query, projection={"_id": False}).sort([("season", 1), ("round", 1), ("driver", 1)])
        results = []
        for doc in cursor:
            doc.pop("_id", None)
            results.append(CleanAirRacePace(**doc))
        logger.debug(f"Retrieved {len(results)} clean air race pace records.")
        return results
    except Exception as e:
        logger.error(f"Error retrieving clean air race pace from MongoDB: {e}")
        raise e
