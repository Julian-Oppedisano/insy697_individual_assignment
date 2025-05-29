import os
import json
import sys # Import sys module
from dotenv import load_dotenv
from apify_client import ApifyClient

def fetch_trump_truth_social_posts_apify(api_key_env_file=".env", output_json_file="trump_posts_raw.json", target_username="realDonaldTrump", max_posts_to_fetch=1000):
    """
    Fetches Donald Trump's Truth Social posts using the Apify Truth Social scraper Actor
    and saves them to a JSON file.
    """
    print(f"Attempting to fetch {max_posts_to_fetch} posts for user '{target_username}' via Apify.")

    # --- Diagnostic for .env file loading ---
    env_file_path = os.path.abspath(api_key_env_file)
    print(f"Diagnostic: Looking for .env file at: {env_file_path}")
    if os.path.exists(env_file_path):
        print(f"Diagnostic: .env file FOUND at {env_file_path}")
        # Keep this minimal for production, or remove if confident
        # try:
        #     with open(env_file_path, 'r') as f_diag:
        #         print(f"Diagnostic: First few lines of .env (or all if short):")
        #         for i, line in enumerate(f_diag):
        #             if i < 1: # Print up to 1 line for minimal log
        #                 print(f"Diagnostic: .env line {i+1} (example): {line.strip()[:20]}...") 
        #             else:
        #                 break
        # except Exception as e_read_diag:
        #     print(f"Diagnostic: Could not read .env for diagnostics: {e_read_diag}")
    else:
        print(f"Diagnostic: .env file NOT FOUND at {env_file_path}")
    # --- End Diagnostic ---

    # --- Load API Key ---
    # print("Diagnostic: Calling load_dotenv()...")
    load_dotenv_success = load_dotenv(dotenv_path=env_file_path, override=True) # Use absolute path
    # print(f"Diagnostic: load_dotenv() returned: {load_dotenv_success}")
    
    apify_api_key = os.getenv("APIFY_API_KEY")
    # print(f"Diagnostic: os.getenv('APIFY_API_KEY') after load_dotenv: '{apify_api_key}'") # Print what was loaded

    if not apify_api_key:
        print(f"Error: APIFY_API_KEY not found in environment after attempting to load from {env_file_path}.")
        print("Please ensure the Apify API key is correctly set with the variable name APIFY_API_KEY in that file.")
        error_data = [{"error": "APIFY_API_KEY not found after load_dotenv."}]
        try:
            with open(output_json_file, 'w') as f:
                json.dump(error_data, f, indent=4)
            print(f"Error details saved to {output_json_file}")
        except Exception as e_save:
            print(f"Error saving error details to {output_json_file}: {e_save}")
        # print("Exiting script after API key check due to missing key.")
        # sys.exit(1) # Exit if key not found - REMOVED FOR NORMAL OPERATION
        return # Return if key not found
    # else:
        # print(f"Found APIFY_API_KEY (from env): '{apify_api_key[:10]}...{apify_api_key[-4:]}'")
        # print("API Key check successful. Exiting before full Apify call as per temporary modification.")
        # sys.exit(0) # Key found, exit successfully for this test - REMOVED FOR NORMAL OPERATION

    print(f"Successfully loaded APIFY_API_KEY.") # Confirmation

    # --- Initialize Apify Client ---
    try:
        client = ApifyClient(apify_api_key)
    except Exception as e:
        print(f"Error initializing ApifyClient: {e}")
        error_data = [{"error": f"Error initializing ApifyClient: {e}"}]
        try:
            with open(output_json_file, 'w') as f:
                json.dump(error_data, f, indent=4)
            print(f"Error details saved to {output_json_file}")
        except Exception as e_save:
            print(f"Error saving error details to {output_json_file}: {e_save}")
        return

    # --- Prepare Actor Input ---
    actor_input = {
        "username": target_username,
        "maxPosts": max_posts_to_fetch,
        "useLastPostId": False, # Get fresh full scrape
        "onlyReplies": False,
        "onlyMedia": False,
        "cleanContent": True
    }
    
    actor_id = "muhammetakkurtt/truth-social-scraper"
    print(f"Running Apify Actor: {actor_id} with input: {actor_input}")

    all_posts = []
    try:
        # Run the Actor and wait for it to finish
        run = client.actor(actor_id).call(run_input=actor_input)
        
        print(f"Actor run initiated. Run ID: {run.get('id')}, Dataset ID: {run.get('defaultDatasetId')}")
        print("Fetching results from dataset... This might take a few minutes.") # Added time warning

        # Fetch Actor results from the run's dataset
        # The .list_items() method handles pagination internally if the dataset is large.
        dataset = client.dataset(run["defaultDatasetId"])
        for item in dataset.iterate_items(): # Iterate through all items in the dataset
            all_posts.append(item)
        
        print(f"Successfully fetched {len(all_posts)} items from the dataset.")
        if not all_posts:
            print("Warning: No items returned from the Apify Actor run.")
            all_posts = [{"warning": "No items returned from Apify Actor for the given input."}]

    except Exception as e:
        print(f"An error occurred during Apify Actor run or data fetching: {e}")
        all_posts = [{"error": f"Apify Actor interaction error: {e}"}]

    # --- Save raw data to JSON ---
    try:
        with open(output_json_file, 'w') as f:
            json.dump(all_posts, f, indent=4)
        print(f"Raw data (or error/warning) saved to {output_json_file}")
    except Exception as e:
        print(f"Error saving data to {output_json_file}: {e}")

if __name__ == "__main__":
    fetch_trump_truth_social_posts_apify()
    print("\nScript finished. Please check the output file and console messages.") 