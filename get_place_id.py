import googlemaps
import os
from dotenv import load_dotenv

def get_place_id_and_save(api_key_file=".env", hotel_name="Montreal Marriott Château Champlain", output_file="hotel_place_id.txt"):
    """
    Retrieves the Google Maps Place ID for a given hotel name and saves it to a file.
    """
    # DIAGNOSTIC: Read and print the relevant line from .env directly
    try:
        with open(api_key_file, 'r') as f:
            print(f"Diagnostics: Reading from {api_key_file}")
            for line in f:
                if "GOOGLE_MAPS_API_KEY" in line:
                    print(f"Diagnostics: Found line: {line.strip()}")
                    break # Found it, no need to read further
            else:
                 print(f"Diagnostics: GOOGLE_MAPS_API_KEY not found in {api_key_file} during direct read.")
    except Exception as e:
        print(f"Diagnostics: Error reading {api_key_file} directly: {e}")

    # Load API key from the specified .env file
    load_dotenv(dotenv_path=api_key_file, override=True)
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    print(f"Attempting to use API Key: '{api_key}'")

    if not api_key:
        print(f"Error: GOOGLE_MAPS_API_KEY not found in {api_key_file}.")
        print("Please ensure the API key is correctly set in the file with the variable name GOOGLE_MAPS_API_KEY.")
        return

    gmaps = googlemaps.Client(key=api_key)

    try:
        # Find place by text query
        places_result = gmaps.find_place(input=hotel_name, input_type="textquery", fields=["place_id", "name"])
        
        if places_result and places_result.get("candidates"):
            candidate = places_result["candidates"][0] # Assuming the first result is the correct one
            place_id = candidate.get("place_id")
            name = candidate.get("name")
            
            if place_id:
                print(f"Found Place ID for '{name}': {place_id}")
                with open(output_file, "w") as f:
                    f.write(place_id)
                print(f"Place ID saved to {output_file}")
            else:
                print(f"Could not find Place ID for '{hotel_name}'.")
        else:
            print(f"No results found for '{hotel_name}'.")
            if places_result:
                print(f"API Response Status: {places_result.get('status')}")
                if places_result.get('error_message'):
                    print(f"API Error Message: {places_result.get('error_message')}")


    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Ensure python-dotenv is installed, as it's used for .env file handling.
    # The main dependencies (including googlemaps) were installed in T04.
    # We need to add python-dotenv.
    try:
        import dotenv
    except ImportError:
        print("python-dotenv library not found. Please install it by running:")
        print("source venv/bin/activate && pip install python-dotenv && deactivate")
        exit(1)
        
    get_place_id_and_save(api_key_file=".env") 