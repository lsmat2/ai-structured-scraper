# For a specific inputted directory, access each json file and process it by loading the data into a dict, removing the 'id' field if it exists, then saving the file
import os
import json
from typing import Dict, Any

def remove_ids_from_json_files(directory: str) -> None:
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


if __name__ == "__main__":
    target_directory = input("Enter the directory containing JSON files: ").strip()
    if os.path.isdir(target_directory):
        remove_ids_from_json_files(target_directory)
    else:
        print(f"The directory {target_directory} does not exist.")