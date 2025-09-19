# Backend client class for interacting with the Place Scraper API
import os
import json
import requests
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

class BackendClient:
    """A client for interacting with the backend API for place management."""
    
    def __init__(self, api_url: Optional[str] = None):
        """Initialize the backend client with API URL."""
        self.api_url = api_url or os.getenv("BACKEND_API_URL")
        if not self.api_url:
            raise ValueError("BACKEND_API_URL must be provided either as parameter or environment variable")
    
    def remove_ids_from_json_files(self, directory: str) -> None:
        """Remove 'id' fields from all JSON files in the specified directory."""
        for root, _, files in os.walk(directory):
            for filename in files:
                if filename.endswith(".json"):
                    full_path = os.path.join(root, filename)
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        
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
        """Fetch place data from backend."""
        url = f"{self.api_url}/api/places/{place_id}"

        try:
            response = requests.get(url, timeout=10)
            return response
        except requests.RequestException as e:
            print(f"Error fetching place data: {e}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON response: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def get_place_id_from_bounds(self, name: str, latitude: float, longitude: float) -> Optional[str]:
        """Fetch place data from backend by geographic bounds."""
        # Params should be structured:    ?bounds=SWlat,SWlng,NElat,NElng
        box_distance: float = 0.001  # ~100 meters around the point
        SWlat: float = latitude - box_distance
        SWlng: float = longitude - box_distance
        NElat: float = latitude + box_distance
        NElng: float = longitude + box_distance
        params_string: str = f"?bounds={SWlat},{SWlng},{NElat},{NElng}"
        url: str = f"{self.api_url}/api/places/{params_string}"

        try:
            response = requests.get(url, timeout=10)
        
        except requests.RequestException as e:
            print(f"Error fetching place data: {e}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON response: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
        if not response.status_code == 200:
            return None
        
        places_list: list[dict] = response.json()
        for place in places_list:
            if place.get("latitude") == latitude and place.get("longitude") == longitude:
                return place.get("id", None)
            elif place.get("name", "").lower() == name.lower():
                return place.get("id", None)

        return None

    def delete_place(self, place_id: int) -> requests.Response:
        """Delete place data from the backend API."""
        url = f"{self.api_url}/api/places/{place_id}"

        try:
            response = requests.delete(url, timeout=10)
            return response
        except requests.RequestException as e:
            print(f"Error deleting place data: {e}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON response: {e}")
        except Exception as e:
            print(f"\nError deleting place data: {e}")

    def update_place(self, place_id: int, place_data: dict) -> requests.Response:
        """Update place data in the backend API."""
        url = f"{self.api_url}/api/places/{place_id}"

        try:
            response = requests.put(url, json=place_data, timeout=10)
            return response
        except requests.RequestException as e:
            print(f"Error updating place data: {e}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON response: {e}")
        except Exception as e:
            print(f"\nError updating place data: {e}")

    def create_place(self, place_data: dict) -> requests.Response:
        """Create place data in the backend API."""
        url = f"{self.api_url}/api/places"

        try:
            response = requests.post(url, json=place_data, timeout=10)
            return response
        except requests.RequestException as e:
            print(f"Error creating place data: {e}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON response: {e}")
        except Exception as e:
            print(f"\nError creating place data: {e}")

    def create_promotion(self, place_id: int, promo_data: dict) -> requests.Response:
        """Create promo data in the backend API."""
        url = f"{self.api_url}/api/places/{place_id}/promotions"

        try:
            response = requests.post(url, json=promo_data, timeout=10)
            return response
        except requests.RequestException as e:
            print(f"Error creating promo data: {e}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON response: {e}")
        except Exception as e:
            print(f"\nError creating promo data: {e}")

