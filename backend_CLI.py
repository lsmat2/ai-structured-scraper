import requests
import os
import json
import sys
from typing import Any, Dict, List, cast
from clean_nearby_places import process_places
from BackendClient import BackendClient

# IMPROVEMENTS: 
# - Include datetime in object to determine time since last request
# - Add retry logic with exponential backoff for failed requests
# - Add logging to file with timestamps

backendClient = BackendClient()


def _process_place_noninteractive(place_id: int, notFoundAction: str, internalServerErrorAction: str, successAction: str) -> None:
    """Process a single place by ID in non-interactive mode."""
    
    print("Non-interactive mode is currently disabled. Please use interactive mode.")
    # allowed_actions = ['d', 'u', 's']
    # if notFoundAction not in allowed_actions or internalServerErrorAction not in allowed_actions or successAction not in allowed_actions:
    #     print(f"Invalid actions specified.")
    #     return

    # try:
    #     place_response = _get_place_by_id(place_id)
    #     status_code = place_response.status_code

    #     if status_code == 404:
    #         if notFoundAction == 'd':
    #             _delete_place(place_id)
    #         elif notFoundAction == 'u':
    #             _update_place(place_id, place_data={})
    #         return

    #     elif status_code == 500:
    #         if internalServerErrorAction == 'd':
    #             _delete_place(place_id)
    #         elif internalServerErrorAction == 'u':
    #             _update_place(place_id, place_data={})
    #         return

    #     elif status_code == 200:
    #         if successAction == 'd':
    #             _delete_place(place_id)
    #         elif successAction == 'u':
    #             _update_place(place_id, place_data={})
    #         return

    # except Exception as e:
    #     print(f"An error occurred while processing place ID {place_id}: {e}")

def _process_place_interactive(place_id:int) -> None:
    """Main function to process a single place by ID."""
    
    try:
        place_response = backendClient.get_place_by_id(place_id)
        status_code = place_response.status_code
       
        if status_code == 404:
            print(f"---404: id {place_id}---")
            return
        
        elif status_code == 500:
            print(f"Place ID {place_id} returning 500, deleting place...")
            backendClient.delete_place(place_id)
            return
        
        elif status_code == 200:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"Place ID {place_id} found. Current data:\n{place_response.json()}")

            action = ''
            while action not in ['d', 's']:
                action = input("Action (delete 'd', skip 's'): ").strip().lower()
                if action == 'd':
                    backendClient.delete_place(place_id)
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
                _process_place_interactive(place_id=id)

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
                _process_place_noninteractive(place_id=id, notFoundAction=not_found_action, internalServerErrorAction=internal_server_error_action, successAction=success_action)

    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except Exception as e:
        print(f"An error occurred while processing existing places: {e}")

def _post_nearbysearch_cleaned_data(filepath:str) -> None:
    """Post cleaned nearby search data to the backend."""

    # Given place data in a file, either update existing place or create new place in backend

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            place_data: Dict[str, Any] = json.load(f)
            if not place_data: raise ValueError("No data found in file")
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON from file {filepath}: {e}")
    except Exception as e:
        raise ValueError(f"Error getting data from file {filepath}: {e}")


    id_local = place_data.pop("id", None)

    id_backend: int | None = backendClient.get_place_id_from_bounds(
        name=place_data.get("name", ""),
        latitude=place_data.get("latitude", 0.0),
        longitude=place_data.get("longitude", 0.0),
    )

    if (id_local is not None) and (id_backend is not None) and (id_local != id_backend):
        print(f"Conflict: Local ID {id_local} does not match backend ID {id_backend}. Updating local ID.")
        place_data["id"] = id_backend
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(place_data, f, indent=2, ensure_ascii=False)
            print(f"Updated local file with new ID {place_data['id']}.")

        
    # 1) Place exists in backend by bounds, update it
    if id_backend:
        print(f"Place ID {id_backend} already exists, updating place...")
        response = backendClient.update_place(id_backend, place_data)
        if response.status_code == 200:
            print(f"Successfully updated place ID {id_backend}\n({response.status_code}): {response.text}")
            return
        else:
            print(f"Failed to update place ID {id_backend}\n({response.status_code}): {response.text}")
            return
    
    # 2) Place does not exist in backend, create it
    print(f"Place does not exist, creating place...")
    response = backendClient.create_place(place_data)
    if response.status_code == 201:
        print(f"Successfully created place\n({response.status_code}): {response.text}")
        if response.json().get("id") is not None: 
            place_data["id"] = response.json().get("id")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(place_data, f, indent=2, ensure_ascii=False)
                print(f"Updated local file with new ID {place_data['id']}.")
    else:
        print(f"Failed to create place ({response.status_code}):{response.text}")
        return

def _post_ai_cleaned_data(ai_data_filepath:str) -> None:
    """Post AI cleaned place data from specified file."""

    try:

        with open(ai_data_filepath, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)
            if not data:
                raise ValueError(f"No data found in file {ai_data_filepath}")

        place_data_raw = data.get("placeData")
        if not place_data_raw or not isinstance(place_data_raw, dict):
            raise ValueError(f"Missing or invalid 'placeData' in file {ai_data_filepath}")
        place_data: Dict[str, Any] = cast(Dict[str, Any], place_data_raw)

        place_id: int | None = place_data.pop("id", None)
        if not place_id:
            raise ValueError(f"Missing 'id' in placeData of file {ai_data_filepath}")
            
        update_place_response: requests.Response = backendClient.update_place(place_id, place_data)
        print(f"Successfully updated place ID {place_id}\n{'-'*60}\n({update_place_response.status_code}): {update_place_response.text}")

        promotion_list_raw = data.get("promoData", None)
        if promotion_list_raw is None:
            print(f"No 'promoData' found in file {ai_data_filepath}")

        else:
            if not isinstance(promotion_list_raw, list):
                raise ValueError(f"'promoData' should be a list of dictionaries in file {ai_data_filepath}")

            promotion_list: List[Any] = cast(List[Any], promotion_list_raw)
            for promo_item in promotion_list:
                if not isinstance(promo_item, dict):
                    raise ValueError(f"Each item in 'promoData' should be a dictionary in file {ai_data_filepath}")

                promo_data: Dict[str, Any] = cast(Dict[str, Any], promo_item)

                # Validate required fields in each promo dictionary
                if "title" not in promo_data or "description" not in promo_data or "hours" not in promo_data:
                    raise ValueError(f"Missing 'title', 'description' or 'hours' in promoData item in file {ai_data_filepath}")

                # If all checks pass, create the promo
                create_promo_response: requests.Response = backendClient.create_promotion(place_id=place_id, promo_data=promo_data)
                print(f"Successfully created promo {promo_data['title']}\n{'-'*60}\n({create_promo_response.status_code}): {create_promo_response.text}")
        
        print(f"Finished processing AI cleaned data from file {ai_data_filepath}")

    except ValueError as e:
        print(f"Value Error processing AI cleaned data: {e}")
    except Exception as e:
        print(f"Unexpected error processing AI cleaned data: {e}")

def process_nearbysearch_data() ->  None:
    """Process nearby search cleaned data to be added to the database."""
    try:
        nearby_data_filepath = input("Enter nearby search cleaned data file path (or 'all' to specify all cleaned files in output directory: output_nearbySearch/): ").strip()

        if (nearby_data_filepath == 'all'):
            for root, dirs, _ in os.walk("output_nearbySearch/"):
                for dir in dirs:
                    print(f"Processing directory: {dir}")
                    subdirectory_path = os.path.join(root, dir)
                    for subroot, _, subfiles in os.walk(subdirectory_path):
                        for subfilename in subfiles:
                            if subfilename.endswith(".json"):
                                process_places(os.path.join(subroot, subfilename))

        else:
            process_places(nearby_data_filepath)

    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except Exception as e:
        print(f"An error occurred while processing nearby search data: {e}")

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
                    for root, _, files in os.walk("output_nearbySearch_cleaned/"):
                        for filename in files:
                            if filename.endswith(".json"):
                                _post_nearbysearch_cleaned_data(os.path.join(root, filename))

                else:
                    _post_nearbysearch_cleaned_data(nearby_data_filepath)

            elif type_of_data_option == 'ai':
                ai_data_filepath = input("Enter AI cleaned data file path (or 'all' to specify all AI cleaned files in output directory: output_nearbySearch_ai_cleaned/): ").strip()

                if (ai_data_filepath == 'all'):
                    for root, _, files in os.walk("output_nearbySearch_ai_cleaned/"):
                        for filename in files:
                            if filename.endswith(".json"):
                                _post_ai_cleaned_data(os.path.join(root, filename))
                else:
                    _post_ai_cleaned_data(ai_data_filepath)

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

    print(f"Welcome to the Place Data CLI!\n{'~'*60}")

    # Top level CLI interaction
    try:
        print(f"""Options:
              'pe') Process Existing, (interact with existing place data in backend)
              'pn') Post New, (add new place data to backend)
              'pns') Process Nearby Search, (interact with local nearby search data)
              'q') Quit\n\n{'~'*60}\n""")

        input_option = ''
        while input_option not in ['pe', 'pn', 'pns', 'q']:
            input_option = input("Select an option('pe', 'pn', 'pns', 'q'): ").strip()

            if input_option == 'pe':
                process_existing_places()

            elif input_option == 'pn':
                post_new_places()

            elif input_option == 'pns':
                process_nearbysearch_data()

            elif input_option == 'q':
                print("Exiting...")
                sys.exit(0)

            input_option = ''

    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Shutting down gracefully.")
        sys.exit(0)

if __name__ == "__main__":
    main()