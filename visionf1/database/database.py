"""
MongoDB database connection and operations for driver standings.
"""

import logging
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from visionf1.models.models import DriverStanding
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

def insert_driver_standings(standings: List[DriverStanding]) -> bool:
    """
    Inserts driver standings into MongoDB (utility function for data migration).
    """
    try:
        # Convert DriverStanding objects to dictionaries
        standings_dict = [standing.model_dump() for standing in standings]

        # Clear the existing collection and insert new data
        driver_standings_collection.delete_many({})
        result = driver_standings_collection.insert_many(standings_dict)
        
        logger.info(f"Inserted {len(result.inserted_ids)} driver standings into MongoDB.")
        return True
        
    except Exception as e:
        logger.error(f"Error inserting driver standings into MongoDB: {e}")
        return False