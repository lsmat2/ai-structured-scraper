"""
Google Places API Data Fetcher (NEW)

Fetches place data from Google Places NearbySearch API (NEW) through POST requests and saves to JSON.
"""

import json
import logging
import os
import sys
from typing import Dict, List
import requests
from dotenv import load_dotenv

from config import FIELD_MASK, INCLUDED_TYPES_FOOD_AND_DRINK

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GooglePlacesAPIError(Exception):
    """Custom exception for Google Places API errors."""
    pass

class PlacesFetcher:
    """Handles fetching and processing data from Google Places API."""
    
    OUTPUT_DIR = "output_nearbySearch"  # Desired Output Directory
    NEARBY_SEARCH_URL = "https://places.googleapis.com/v1/places:searchNearby" # Docs: https://developers.google.com/maps/documentation/places/web-service/nearby-search


    def __init__(self, api_key: str = None):
        """Initialize the PlacesFetcher."""

        load_dotenv()
        self.api_key = api_key or os.getenv("GOOGLE_PLACES_API_KEY")
        if not self.api_key: raise GooglePlacesAPIError( "Google Places API key not found. Set GOOGLE_PLACES_API_KEY environment variable or pass api_key parameter." )

    def _fetch_nearby_places(
            self,
            latitude: float,
            longitude: float,
            radius: float = 100.0, # 0.0 <= radius <= 50000.0 (METERS)
            included_types: list[str] = ["restaurant", "pub", "bar"], # Default types to include
            max_results: int = 1, # 1 <= max_results <= 20 
            field_mask: str = "*"
        ) -> List[Dict]:
        """Fetch nearby places from Google Places API."""

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": field_mask
        }

        payload = {
            "includedPrimaryTypes": included_types,
            # "includedTypes": included_types, # Difference from includedPrimaryTypes is whether it's the primaryType or just in types fields
            "languageCode": "en",
            "rankPreference": "DISTANCE", # Options: DISTANCE, POPULARITY
            "maxResultCount": max_results,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude
                    },
                    "radius": radius
                }
            }
        }
        
        try:
            response = requests.post(self.NEARBY_SEARCH_URL, headers=headers, json=payload)
            response.raise_for_status()  # Raises error if status code is not 2xx
            data = response.json()
            return data.get("places", [])
        
        except requests.RequestException as e:
            raise GooglePlacesAPIError(f"Failed to fetch nearby places: {e}")
        except json.JSONDecodeError as e:
            raise GooglePlacesAPIError(f"Invalid JSON response: {e}")

    def _save_to_file(self, data: List[Dict], filename: str) -> None:
        """Save data to JSON file with error handling."""

        os.makedirs(self.OUTPUT_DIR, exist_ok=True) # Create directory if it doesn't exist
        full_path = os.path.join(self.OUTPUT_DIR, filename) # Full path to the output file

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {filename}")
        except IOError as e:
            logger.error(f"Failed to save data to {filename}: {e}")
            raise

    def fetch_and_save_nearby_places(
            self, 
            latitude: float,
            longitude: float,
            radius: float = 10.0, # 0.0 <= radius <= 50000.0 (METERS)
            included_types: list[str] = ["restaurant", "pub", "bar"], # Default types to include
            max_results: int = 1, # 1 <= max_results <= 20 
            field_mask: str = "*",
        ) -> None:
        """Main processing function to fetch and format places data."""

        logger.info(f"Fetching places near ({latitude}, {longitude}) within {radius}m radius")
        
        try:
            places = self._fetch_nearby_places(
                latitude = latitude,
                longitude = longitude,
                radius = radius,
                included_types = included_types,
                max_results = max_results,
                field_mask = field_mask
            )

            if (len(places) == 0):
                logger.info("No places found. Exiting.")
                return
            
            logger.info(f"Found {len(places)} places")
            output_file = f"{latitude}-{longitude}.json"
            self._save_to_file(data=places, filename=output_file)

            return
            
        except GooglePlacesAPIError as e:
            logger.error(f"Failed to process location: {e}")
            raise

def main():
    """Main function for CLI usage."""

    # CHICAGO           --> 41.8781 -87.6298
    # SAN_FRANCISCO     --> 37.7749 -122.4194

    if len(sys.argv) != 3:
        print("Usage: python filename.py <latitude> <longitude>")
        sys.exit(1)

    lat = sys.argv[1]
    lon = sys.argv[2]
    lat_rounded = round(float(lat), 7)
    lon_rounded = round(float(lon), 7)

    # logger.info(f"Included Types: {INCLUDED_TYPES_FOOD_AND_DRINK}")
    # logger.info(f"Field Mask: {FIELD_MASK}")

    try:
        fetcher = PlacesFetcher()
        fetcher.fetch_and_save_nearby_places(
            latitude=lat_rounded, 
            longitude=lon_rounded, 
            radius=5000.0, # 0.0 <= radius <= 50000.0 (METERS)
            included_types=INCLUDED_TYPES_FOOD_AND_DRINK, 
            # included_types=['bar', 'pub'],
            max_results=20, # 1 <= max_results <= 20 
            field_mask=FIELD_MASK,
        )

    except GooglePlacesAPIError as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()