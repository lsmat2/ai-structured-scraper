import requests
import os
import json
import sys
from typing import Dict, List
from dotenv import load_dotenv

# IMPROVEMENTS: 
# - Include datetime in object to determine time since last request
# - Filter out non-english places

load_dotenv()
BACKEND_API_URL = os.getenv("BACKEND_API_URL")

class GooglePlacesAPIError(Exception):
    """Custom exception for Google Places API errors."""
    pass

def _get_nearby_places(filename:str) -> List[Dict]:
    """Fetch place data from local file."""

    with open(filename, "r") as f:
        places: List[Dict] = json.load(f)

    return places

def _format_place_data(place_data:Dict) -> Dict:
    """Formats google places data to be compatible with backend. Object may include 
    'missing_fields' field with any omitted fields from the original place_data. """

    formatted_place_data: Dict = {}
    missing_fields: List[str] = []

    # Google Places API id (should always be present)
    google_places_id: str = place_data.get("id")
    if google_places_id is None : missing_fields.append("google_places_id")
    else: formatted_place_data["google_places_id"] = google_places_id

    # Display Name (should always be present)
    name: str = place_data.get("displayName", {}).get("text")
    if name is None: missing_fields.append("name")
    else: formatted_place_data["name"] = name

    # Coordinates (should always be present)
    latitude: float = place_data.get("location", {}).get("latitude")
    longitude: float = place_data.get("location", {}).get("longitude")
    if latitude is None or longitude is None:
        missing_fields.append("latitude")
        missing_fields.append("longitude")
    else:

        formatted_place_data["latitude"] = round(latitude, 6)
        formatted_place_data["longitude"] = round(longitude, 6)

    # Types
    primaryType = place_data.get("primaryType")
    if primaryType is None: missing_fields.append("primaryType")
    else: formatted_place_data["primaryType"] = primaryType
    types: List[str] = place_data.get("types")
    if types is None or len(types) == 0: missing_fields.append("types")
    else: formatted_place_data["types"] = [t for t in types if t not in ["point_of_interest", "establishment"]]

    # Address
    postalAddress: Dict = place_data.get("postalAddress")
    if postalAddress is None: missing_fields.append("postalAddress")
    else:
        city: str = postalAddress.get("locality")
        if city is None: missing_fields.append("city")
        else: formatted_place_data["city"] = city

        state_code: str = postalAddress.get("administrativeArea")
        if state_code is None: missing_fields.append("state_code")
        else: formatted_place_data["state_code"] = state_code
    
        zip = postalAddress.get("postalCode")
        if zip is None: missing_fields.append("zip")
        else:
            if len(zip) == 5: zip = int(zip)
            elif len(zip) == 10 and zip[5] == '-': zip = int(zip[0:5])
            formatted_place_data["zip"] = zip

        street: str = postalAddress.get("addressLines")
        if street is None or len(street) == 0: missing_fields.append("street")
        else: formatted_place_data["street"] = street[0]


    # Hours
    periods = place_data.get("regularOpeningHours", {}).get("periods", [])
    if periods is None or len(periods) == 0: missing_fields.append("hours")
    else:
        day_map: Dict = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'}
        formatted_weekly_hours: List[Dict] = []
        for period in periods:
            if period.get('open') is None or period.get('close') is None: raise(GooglePlacesAPIError("Invalid hours format from Google Places API"))
            else: 
                day:int = period['open'].get('day')
                open_hour:int = period['open'].get('hour')
                open_minute:int = period['open'].get('minute')
                open_time:int = open_hour * 100 + open_minute

                close_hour:int = period['close'].get('hour')
                close_minute:int = period['close'].get('minute')
                close_time:int = close_hour * 100 + close_minute

                if day is not None and day in day_map:
                    formatted_weekly_hours.append({
                        "day": day_map[day],
                        "open_hour": open_time,
                        "close_hour": close_time
                    })
                    
        formatted_place_data["hours"] = formatted_weekly_hours

    # Contact Info
    phone = place_data.get("nationalPhoneNumber")
    if phone is None: missing_fields.append("phone")  
    else: formatted_place_data["phone"] = phone
    website = place_data.get("websiteUri")
    if website is None: missing_fields.append("website")
    else: formatted_place_data["website"] = website


    if len(missing_fields) > 0: formatted_place_data['missing_fields'] = missing_fields
    return formatted_place_data


def _post_nearby_places(places:List[Dict]) -> None:
    """Post place data to the backend API from specified file."""

    url = f"{BACKEND_API_URL}/api/places"
    print(f"Posting place data to: {url}")
    
    for i, place_data in enumerate(places, 1):

        # os.system('cls' if os.name == 'nt' else 'clear')
        # print(f"{"="*60}\nProcessing place {i} OF {len(places)}\n{"="*60}")
        print(f"Processing place {i} OF {len(places)}")
        
        # Ensure place is operational before formatting/posting
        place_status: str = place_data.get("businessStatus")
        if place_status != "OPERATIONAL":
            print(f"Skipping place {i}: ({place_status})")
            continue

        formatted_place_data = _format_place_data(place_data=place_data)
        # _display_formatted_place_data(formatted_place_data=formatted_place_data)

        # Manual approval to post place
        if input("\nDo you want to post this place data? (y/n): ").lower() != 'y': continue
        print(f"Posting place {i}: {formatted_place_data['name']} to backend...")

        try:
            # print("\nSending request...")
            response = requests.post(url, json=formatted_place_data, timeout=10)
            print(f"Response ({response.status_code}) : {response.text}")

        except Exception as e:
            print(f"\nError posting place data: {e}")
        
        input("\n Press Enter to continue...")


def _save_nearby_places(places: List[Dict]) -> None:
    """Save formatted place data as individual JSON files."""
    
    output_dir = "output_nearbySearch_cleaned"
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    for i, place_data in enumerate(places, 1):
        print(f"Processing place {i} OF {len(places)}")
        
        # Ensure place is operational before formatting/saving
        place_status: str = place_data.get("businessStatus")
        if place_status != "OPERATIONAL":
            print(f"Skipping place {place_data.get('displayName', {}).get('text', 'NO NAME FOUND')}: ({place_status})")
            continue

        formatted_place_data = _format_place_data(place_data=place_data)
        if formatted_place_data.get('missing_fields') is not None:
            print(f"Place {formatted_place_data.get('name', 'NO_NAME_FOUND')} is missing required fields: {formatted_place_data['missing_fields']}")
            if input("Do you want to save this place data anyway? (y/n): ").lower() != 'y': continue
            del formatted_place_data['missing_fields']

        # Create filename from place name (sanitize for filesystem)
        place_name = formatted_place_data['name']
        # Remove/replace characters that aren't filesystem-safe
        safe_filename = "".join(char for char in place_name if char.isalnum() or char in (' ', '-', '_')).rstrip()
        safe_filename = safe_filename.replace(' ', '_')
        filename = f"{safe_filename}.json"
        filepath = os.path.join(output_dir, filename)
        
        print(f"Saving place {i}: {place_name} to {filename}")
        
        try:
            with open(filepath, 'w') as f:
                json.dump(formatted_place_data, f, indent=2)
            print(f"Successfully saved: {filename}")
            
        except Exception as e:
            print(f"Error saving place data: {e}")

        input("\n Press Enter to continue...")


def process_places(filename: str):
    """Main function to process places from a JSON file."""
    
    try:
        
        places = _get_nearby_places(filename)
        # _post_nearby_places(places)
        _save_nearby_places(places)

    except FileNotFoundError:
        print(f"File not found: {filename}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {filename}")
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    """Main function to run the place data posting script."""

    if len(sys.argv) != 2:
        print("Usage: python script.py <json_file>")
        sys.exit(1)
    
    filename:str = sys.argv[1]

    try:
        process_places(filename)

    except FileNotFoundError:
        print(f"File not found: {filename}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {filename}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
    
if __name__ == "__main__":
    main()