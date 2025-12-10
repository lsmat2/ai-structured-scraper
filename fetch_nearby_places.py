"""
Google Places API Data Fetcher (NEW)

Fetches place data from Google Places NearbySearch API (NEW) through POST requests and saves to JSON.
"""

import json
import logging
import os
import sys
from typing import Dict, List, Optional, Any
import requests
from dotenv import load_dotenv

from config import FIELD_MASK, INCLUDED_TYPES_FOOD_AND_DRINK

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PlacesFetcher:
    """Handles fetching and processing data from Google Places API."""
    
    OUTPUT_DIR = "output_nearbySearch"  # Desired Output Directory
    NEARBY_SEARCH_URL = "https://places.googleapis.com/v1/places:searchNearby" # Docs: https://developers.google.com/maps/documentation/places/web-service/nearby-search


    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize the PlacesFetcher.

        Raises:
            ValueError: If API key is not provided
        """
        load_dotenv()
        api_key_value = api_key or os.getenv("GOOGLE_PLACES_API_KEY")
        if not api_key_value:
            raise ValueError(
                "Google Places API key not found. Set GOOGLE_PLACES_API_KEY "
                "environment variable or pass api_key parameter."
            )
        self.api_key: str = api_key_value

    def _fetch_nearby_places(
            self,
            latitude: float,
            longitude: float,
            radius: float = 100.0,
            included_types: List[str] = ["restaurant", "pub", "bar"],
            max_results: int = 1,
            field_mask: str = "*"
        ) -> List[Dict[str, Any]]:
        """Fetch nearby places from Google Places API.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius: Search radius in meters (0.0 to 50000.0)
            included_types: List of place types to include
            max_results: Maximum number of results (1 to 20)
            field_mask: Fields to return in response

        Returns:
            List of place dictionaries

        Raises:
            requests.RequestException: If the API request fails
            json.JSONDecodeError: If response cannot be parsed
        """
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": field_mask
        }

        payload: Dict[str, Any] = {
            "includedPrimaryTypes": included_types,
            "languageCode": "en",
            "rankPreference": "DISTANCE",
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

        response = requests.post(self.NEARBY_SEARCH_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("places", [])

    def _save_to_file(self, data: List[Dict[str, Any]], filename: str) -> None:
        """Save data to JSON file.

        Raises:
            IOError: If file cannot be written
        """
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        full_path = os.path.join(self.OUTPUT_DIR, filename)

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
            radius: float = 10.0,
            included_types: List[str] = ["restaurant", "pub", "bar"],
            max_results: int = 1,
            field_mask: str = "*",
        ) -> None:
        """Fetch nearby places and save to JSON file.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius: Search radius in meters (0.0 to 50000.0)
            included_types: List of place types to include
            max_results: Maximum number of results (1 to 20)
            field_mask: Fields to return in response

        Raises:
            requests.RequestException: If the API request fails
            json.JSONDecodeError: If response cannot be parsed
            IOError: If file cannot be written
        """
        logger.info(f"Fetching places near ({latitude}, {longitude}) within {radius}m radius")

        places = self._fetch_nearby_places(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            included_types=included_types,
            max_results=max_results,
            field_mask=field_mask
        )

        if len(places) == 0:
            logger.info("No places found. Exiting.")
            return

        logger.info(f"Found {len(places)} places")
        output_file = f"{latitude}-{longitude}.json"
        self._save_to_file(data=places, filename=output_file)

def main() -> None:
    """Main function for CLI usage.

    Usage: python filename.py <latitude> <longitude>
    """
    if len(sys.argv) != 3:
        print("Usage: python filename.py <latitude> <longitude>")
        sys.exit(1)

    lat_rounded = round(float(sys.argv[1]), 7)
    lon_rounded = round(float(sys.argv[2]), 7)

    try:
        fetcher = PlacesFetcher()
        fetcher.fetch_and_save_nearby_places(
            latitude=lat_rounded,
            longitude=lon_rounded,
            radius=5000.0,
            included_types=INCLUDED_TYPES_FOOD_AND_DRINK,
            max_results=20,
            field_mask=FIELD_MASK,
        )
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()