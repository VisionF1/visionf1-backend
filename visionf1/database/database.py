"""
MongoDB database connection and operations for driver standings.
"""

import logging
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from visionf1.models.models import DriverStanding, TeamStanding, Driver, UpcomingGP
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
