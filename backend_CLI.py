import requests
import os
import json
import sys
from dotenv import load_dotenv

# IMPROVEMENTS: 
# - Include datetime in object to determine time since last request

load_dotenv()
BACKEND_API_URL = os.getenv("BACKEND_API_URL")

def _get_place_by_id(place_id:int) -> requests.Response:
    """Fetch place data from backend."""
    url = f"{BACKEND_API_URL}/api/places/{place_id}"
    # print(f"Fetching place data from: {url}")

    try:
        response = requests.get(url, timeout=10)
        return response
    except requests.RequestException as e:
        print(f"Error fetching place data: {e}")
    except json.JSONDecodeError as e:
        print(f"Invalid JSON response: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def _delete_place(place_id:int) -> requests.Response:
    """Delete place data from the backend API."""
    url = f"{BACKEND_API_URL}/api/places/{place_id}"
    # print(f"Deleting place data from: {url}")

    try:
        response = requests.delete(url, timeout=10)
        return response
    except requests.RequestException as e:
        print(f"Error deleting place data: {e}")
    except json.JSONDecodeError as e:
        print(f"Invalid JSON response: {e}")
    except Exception as e:
        print(f"\nError deleting place data: {e}")

def _update_place(place_id:int, place_data:dict) -> requests.Response:
    """Update place data in the backend API."""
    url = f"{BACKEND_API_URL}/api/places/{place_id}"
    # print(f"Updating place data at: {url}")

    try:
        response = requests.put(url, json=place_data, timeout=10)
        return response
    except requests.RequestException as e:
        print(f"Error updating place data: {e}")
    except json.JSONDecodeError as e:
        print(f"Invalid JSON response: {e}")
    except Exception as e:
        print(f"\nError updating place data: {e}")



def process_place(place_id:int, isInteractive:bool = True) -> None:
    """Main function to process a single place by ID."""
    
    try:
        place_response = _get_place_by_id(place_id)
        status_code = place_response.status_code
       
        if isInteractive: # Interactive mode
            action = ''
            while action not in ['d', 'u', 's']:
                action = input("\nDelete place: 'd'\nUpdate place w/ default hours: 'u'\nSkip place: 's'\n").strip().lower()
                if action == 'u':
                    _update_place(place_id)
                elif action == 'd':
                    _delete_place(place_id)
                elif action == 's':
                    print(f"Skipping place ID: {place_id}")
                else:
                    print("Invalid action. Please choose 'd', 'u', or 's'.")
            os.system('cls' if os.name == 'nt' else 'clear')

        else: # Automatic actions based on status code
            if status_code == 404:
                print(f"Place ID {place_id} not found. Skipping.")
                return
            elif status_code == 200:
                print(f"Place ID {place_id} found, still deleting lol.")
                _delete_place(place_id)
                return
            elif status_code == 500:
                print(f"Place ID {place_id} returning 500. Deleting place.")
                _delete_place(place_id)

    except Exception as e:
        print(f"An error occurred while processing place ID {place_id}: {e}")


def post_ai_cleaned_data(ai_data_filepath:str) -> None:
    """Post AI cleaned place data from specified file."""

    try:
        with open(ai_data_filepath, "r", encoding="utf-8") as f:
            data:dict = json.load(f)
    except Exception as e:
        raise ValueError(f"Failed to read or parse file {ai_data_filepath}: {e}")

    if data.get("placeData") is None: raise ValueError(f"Missing 'placeData' in file {ai_data_filepath}")
    place_data = data["placeData"]

    if data.get("eventData") is not None:
        event_data = data["eventData"]
    
    if data.get("promoData") is not None:
        promo_data = data["promoData"]

    if data.get("menuData") is not None:
        menu_data = data["menuData"]

    print(f"{'~' * 60}\nDisplaying formatted place data for: {place_data['name']}\n")
    if event_data is not None: print(f"Event Data\n{'~' * 60}\n {event_data}")
    if promo_data is not None: print(f"Promo Data\n{'~' * 60}\n {promo_data}")
    if menu_data is not None: print(f"Menu Data\n{'~' * 60}\n {menu_data}")

    # Manual approval to post place
    if input("\nDo you want to update this place data? (y/n): ").lower() != 'y': return

    try:
        print("\nSending request...")

        response = _update_place(place_id=data["id"], place_data=place_data)

        print(f"Response ({response.status_code}) : {response.text}")

    except Exception as e:
        print(f"\nError posting place data: {e}")



def main():
    """Main function to run the place data posting script."""


    try:
        for i in range(895, 1083):
            print(f"{'='*60}\nProcessing place ID: {i}")
            process_place(i, isInteractive=True)  # Set to True for interactive mode

    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        sys.exit(0)

    
if __name__ == "__main__":
    main()