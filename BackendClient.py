# Backend client class for interacting with the Place Scraper API
import os
import json
import requests
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
load_dotenv()

class BackendClient:
    """A client for interacting with the backend API for place management."""
    
    def __init__(self, api_url: Optional[str] = None) -> None:
        """Initialize the backend client with API URL."""
        self.api_url: Optional[str] = api_url or os.getenv("BACKEND_API_URL")
        if not self.api_url:
            raise ValueError("BACKEND_API_URL must be provided either as parameter or environment variable")
    
    def remove_ids_from_json_files(self, directory: str) -> None:
        """Remove 'id' fields from all JSON files in the specified directory."""
        for root, _, files in os.walk(directory):
            root_path: str = root
            filenames: List[str] = files
            for filename in filenames:
                if filename.endswith(".json"):
                    full_path: str = os.path.join(root_path, filename)
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            data: Any = json.load(f)
                        
                        if isinstance(data, dict) and 'id' in data:
                            del data['id']
                            with open(full_path, "w", encoding="utf-8") as f:
                                json.dump(data, f, indent=2, ensure_ascii=False)
                            print(f"Removed 'id' from {full_path}")
                        else:
                            print(f"No 'id' field found in {full_path}")

                    except (IOError, json.JSONDecodeError) as e:
                        print(f"Error processing {full_path}: {e}")

    def get_place_by_id(self, place_id: int) -> requests.Response:
        """Fetch place data from backend.

        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.api_url}/api/places/{place_id}"
        response = requests.get(url, timeout=10)
        return response

    def get_place_id_from_bounds(self, name: str, latitude: float, longitude: float) -> Optional[int]:
        """Fetch place data from backend by geographic bounds.

        Returns:
            Place ID (integer) if found, None if not found

        Raises:
            requests.RequestException: If the request fails
            json.JSONDecodeError: If response cannot be parsed as JSON
        """
        # Params should be structured:    ?bounds=SWlat,SWlng,NElat,NElng
        box_distance: float = 0.001  # ~100 meters around the point
        SWlat: float = latitude - box_distance
        SWlng: float = longitude - box_distance
        NElat: float = latitude + box_distance
        NElng: float = longitude + box_distance
        params_string: str = f"?bounds={SWlat},{SWlng},{NElat},{NElng}"
        url: str = f"{self.api_url}/api/places/{params_string}"

        response: requests.Response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        try:
            places_list: List[Dict[str, Any]] = response.json()
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Failed to parse JSON response from {url}",
                e.doc,
                e.pos
            )

        for place in places_list:
            if place.get("latitude") == latitude and place.get("longitude") == longitude:
                return place.get("id", None)
            elif place.get("name", "").lower() == name.lower():
                return place.get("id", None)

        return None

    def delete_place(self, place_id: int) -> requests.Response:
        """Delete place data from the backend API.

        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.api_url}/api/places/{place_id}"
        response = requests.delete(url, timeout=10)
        return response

    def update_place(self, place_id: int, place_data: Dict[str, Any]) -> requests.Response:
        """Update place data in the backend API.

        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.api_url}/api/places/{place_id}"
        response = requests.put(url, json=place_data, timeout=10)
        return response

    def create_place(self, place_data: Dict[str, Any]) -> requests.Response:
        """Create place data in the backend API.

        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.api_url}/api/places"
        response = requests.post(url, json=place_data, timeout=10)
        return response

    def create_promotion(self, place_id: int, promo_data: Dict[str, Any]) -> requests.Response:
        """Create promo data in the backend API.

        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.api_url}/api/places/{place_id}/promotions"
        response = requests.post(url, json=promo_data, timeout=10)
        return response

