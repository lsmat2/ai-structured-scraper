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

    try:
        response = requests.put(url, json=place_data, timeout=10)
        return response
    except requests.RequestException as e:
        print(f"Error updating place data: {e}")
    except json.JSONDecodeError as e:
        print(f"Invalid JSON response: {e}")
    except Exception as e:
        print(f"\nError updating place data: {e}")

def process_place_noninteractive(place_id: int, notFoundAction: str, internalServerErrorAction: str, successAction: str) -> None:
    """Process a single place by ID in non-interactive mode."""

    allowed_actions = ['d', 'u', 's']
    if notFoundAction not in allowed_actions or internalServerErrorAction not in allowed_actions or successAction not in allowed_actions:
        print(f"Invalid actions specified.")
        return

    try:
        place_response = _get_place_by_id(place_id)
        status_code = place_response.status_code

        if status_code == 404:
            if notFoundAction == 'd':
                _delete_place(place_id)
            elif notFoundAction == 'u':
                _update_place(place_id, place_data={})
            return

        elif status_code == 500:
            if internalServerErrorAction == 'd':
                _delete_place(place_id)
            elif internalServerErrorAction == 'u':
                _update_place(place_id, place_data={})
            return

        elif status_code == 200:
            if successAction == 'd':
                _delete_place(place_id)
            elif successAction == 'u':
                _update_place(place_id, place_data={})
            return

    except Exception as e:
        print(f"An error occurred while processing place ID {place_id}: {e}")

def process_place_interactive(place_id:int) -> None:
    """Main function to process a single place by ID."""
    
    try:
        place_response = _get_place_by_id(place_id)
        status_code = place_response.status_code
       
        if status_code == 404:
            print(f"---404: id {place_id}---")
            return
        
        elif status_code == 500:
            print(f"Place ID {place_id} returning 500, deleting place...")
            _delete_place(place_id)
            return
        
        elif status_code == 200:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"Place ID {place_id} found. Current data:\n{place_response.json()}")

            action = ''
            while action not in ['d', 'u', 's']:
                action = input("Action (delete 'd', update 'u', skip 's'): ").strip().lower()
                if action == 'u':
                    _update_place(place_id)
                elif action == 'd':
                    _delete_place(place_id)
                elif action == 's':
                    print(f"Skipping place ID: {place_id}")
                else:
                    print("Invalid action. Please choose 'd', 'u', or 's'.")

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

def process_existing_places() -> None:
    """Process existing places in the database."""
    try:
        start_id = int(input("Enter start place ID: "))
        end_id = int(input("Enter end place ID: "))
        is_interactive = bool(input("Interactive? (y/n): ") == 'y')

        if (is_interactive):
            for id in range(start_id, end_id):
                process_place_interactive(place_id=id)

        else:
            not_found_action = input("Action on 404 Not Found? (d=delete, s=skip, u=update): ").strip().lower()
            while not_found_action not in ['d', 's', 'u']:
                not_found_action = input("Invalid action. Please enter 'd', 's', or 'u': ").strip().lower()

            internal_server_error_action = input("Action on 500 Internal Server Error? (d=delete, s=skip, u=update): ").strip().lower()
            while internal_server_error_action not in ['d', 's', 'u']:
                internal_server_error_action = input("Invalid action. Please enter 'd', 's', or 'u': ").strip().lower()

            success_action = input("Action on 200 Success? (d=delete, s=skip, u=update): ").strip().lower()
            while success_action not in ['d', 's', 'u']:
                success_action = input("Invalid action. Please enter 'd', 's', or 'u': ").strip().lower()

            for id in range(start_id, end_id):
                process_place_noninteractive(place_id=id, notFoundAction=not_found_action, internalServerErrorAction=internal_server_error_action, successAction=success_action)
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except Exception as e:
        print(f"An error occurred while processing existing places: {e}")

def main():
    """Main function to run the place data posting script."""
    
    if (len(sys.argv) != 1):
        print("Usage: python backend_CLI.py")
        sys.exit(1)

    print(f"Welcome to the Place Data Management CLI!\n{'~'*60}")

    # Top level CLI interaction
    try:
        print(f"Options:\n1) Interact with existing place data in backend\n2) Add new place data to backend\n{'~'*60}\n")
        
        input_option = int(input("Select an option(1-2): ").strip())
        
        if input_option == 1:
            process_existing_places()
        elif input_option == 2:
            ai_data_filepath = input("Enter place data file path: ").strip()
            post_ai_cleaned_data(ai_data_filepath)

        else:
            print("Invalid option selected.")

    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Shutting down gracefully.")
        sys.exit(0)

    
if __name__ == "__main__":
    main()