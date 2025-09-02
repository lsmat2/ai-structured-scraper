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

def _create_place(place_data:dict) -> requests.Response:
    """Create place data in the backend API."""
    url = f"{BACKEND_API_URL}/api/places"

    try:
        response = requests.post(url, json=place_data, timeout=10)
        return response
    except requests.RequestException as e:
        print(f"Error creating place data: {e}")
    except json.JSONDecodeError as e:
        print(f"Invalid JSON response: {e}")
    except Exception as e:
        print(f"\nError creating place data: {e}")


def _create_promo(place_id: int, promo_data:dict) -> requests.Response:
    """Create promo data in the backend API."""
    url = f"{BACKEND_API_URL}/api/places/{place_id}/promotions"

    try:
        response = requests.post(url, json=promo_data, timeout=10)
        return response
    except requests.RequestException as e:
        print(f"Error creating promo data: {e}")
    except json.JSONDecodeError as e:
        print(f"Invalid JSON response: {e}")
    except Exception as e:
        print(f"\nError creating promo data: {e}")

    

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

def post_nearbysearch_cleaned_data(filepath:str) -> None:
    """Post cleaned nearby search data to the backend."""

    try:

        with open(filepath, "r", encoding="utf-8") as f:
            data:dict = json.load(f)
        
        if not data: raise ValueError("No data found in file")

        id = data.get("id")
        if not id:
            print(f"No existing id in local object, creating new place...")
            response = _create_place(data)

            if response.status_code == 201:
                print(f"Successfully created new place\n({response.status_code}): {response.text}")
                
                if response.json().get("id") is not None: 
                    
                    data["id"] = response.json().get("id")

                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                        print(f"Updated local file with new ID.")

            else:
                print(f"Failed to create place ({response.status_code}):{response.text}")
        else:
            print(f"Place ID {id} already exists, updating place...")
            response = _update_place(id, data)

            if response.status_code == 200:
                print(f"Successfully updated place ID {id}\n({response.status_code}): {response.text}")
            else:
                print(f"Failed to update place ID {id}\n({response.status_code}): {response.text}")

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from file {filepath}: {e}")
    except Exception as e:
        print(f"Error posting nearby search data: {e}")

def post_ai_cleaned_data(ai_data_filepath:str) -> None:
    """Post AI cleaned place data from specified file."""

    try:

        with open(ai_data_filepath, "r", encoding="utf-8") as f:
            data:dict = json.load(f)
        
        if not data: 
            raise ValueError(f"No data found in file {ai_data_filepath}")
        
        place_data = data.get("placeData")
        if not place_data:
            raise ValueError(f"Missing 'placeData' in file {ai_data_filepath}")
        
        place_id = place_data.get("id")
        if not place_id:
            raise ValueError(f"Missing 'id' in placeData of file {ai_data_filepath}")
            
        update_place_response: requests.Response = _update_place(place_id, place_data)
        print(f"Successfully updated place ID {place_id}\n{'-'*60}\n({update_place_response.status_code}): {update_place_response.text}")

        promotion_list = data.get("promoData", None)
        if promotion_list is None:
            print(f"No 'promoData' found in file {ai_data_filepath}")

        else:
            if not isinstance(promotion_list, list):
                raise ValueError(f"'promoData' should be a list of dictionaries in file {ai_data_filepath}")

            for promo_data in promotion_list:
                if not isinstance(promo_data, dict):
                    raise ValueError(f"Each item in 'promoData' should be a dictionary in file {ai_data_filepath}")

                # Validate required fields in each promo dictionary
                if "title" not in promo_data or "description" not in promo_data or "hours" not in promo_data:
                    raise ValueError(f"Missing 'title', 'description' or 'hours' in promoData item in file {ai_data_filepath}")

                # If all checks pass, create the promo
                create_promo_response: requests.Response = _create_promo(place_id=place_id, promo_data=promo_data)
                print(f"Successfully created promo {promo_data['title']}\n{'-'*60}\n({create_promo_response.status_code}): {create_promo_response.text}")
        
        print(f"Finished processing AI cleaned data from file {ai_data_filepath}")

    except ValueError as e:
        print(f"Value Error processing AI cleaned data: {e}")
    except Exception as e:
        print(f"Unexpected error processing AI cleaned data: {e}")


def post_new_places() -> None:
    """Process new places to be added to the database."""
    try:
        print(f"\nSelect the type of data to add\n'ns') nearby search cleaned data \n'ai') AI cleaned data \n'q') Cancel/Exit\n{'~' * 60}")

        type_of_data_option = ''
        while type_of_data_option not in ['ns', 'ai', 'q']:

            type_of_data_option = input("\nOption (ns, ai, q): ").strip()

            if type_of_data_option == 'ns':
                nearby_data_filepath = input("Enter nearby search cleaned data file path (or 'all' to specify all cleaned files in output directory: output_nearbySearch_cleaned/): ").strip()

                if (nearby_data_filepath == 'all'):
                    for root, dirs, files in os.walk("output_nearbySearch_cleaned/"):
                        for filename in files:
                            if filename.endswith(".json"): 
                                post_nearbysearch_cleaned_data(os.path.join(root, filename))

                else:
                    post_nearbysearch_cleaned_data(nearby_data_filepath)

            elif type_of_data_option == 'ai':
                ai_data_filepath = input("Enter AI cleaned data file path (or 'all' to specify all AI cleaned files in output directory: output_nearbySearch_ai_cleaned/): ").strip()

                if (ai_data_filepath == 'all'):
                    for root, dirs, files in os.walk("output_nearbySearch_ai_cleaned/"):
                        for filename in files:
                            if filename.endswith(".json"):
                                post_ai_cleaned_data(os.path.join(root, filename))
                else:
                    post_ai_cleaned_data(ai_data_filepath)

            elif type_of_data_option == 'q':
                print("Cancelling...")
                return
            
            type_of_data_option = ''

    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except Exception as e:
        print(f"An error occurred while processing new places: {e}")


def main():
    """Main function to run the place data posting script."""
    
    if (len(sys.argv) != 1):
        print("Usage: python backend_CLI.py")
        sys.exit(1)

    print(f"Welcome to the Place Data Management CLI!\n{'~'*60}")

    # Top level CLI interaction
    try:
        print(f"Options:\n'pe') Process Existing, (interact with existing place data in backend)\n'pn') Post New, (add new place data to backend)\n'q') Quit\n{'~'*60}\n")

        input_option = ''
        while input_option not in ['pe', 'pn', 'q']:
            input_option = input("Select an option('pe', 'pn', 'q'): ").strip()

            if input_option == 'pe':
                process_existing_places()

            elif input_option == 'pn':
                post_new_places()

            elif input_option == 'q':
                print("Exiting...")
                sys.exit(0)

            input_option = ''

    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Shutting down gracefully.")
        sys.exit(0)

if __name__ == "__main__":
    main()