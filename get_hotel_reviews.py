import os
import pandas as pd
# import serpapi # Keep this for the new client style
from dotenv import load_dotenv

# For the serpapi.Client() style, we will import the main module
import serpapi # This is the primary change for the client

def fetch_reviews_and_save(place_id_file="hotel_place_id.txt", 
                           api_key_env_file=".env", 
                           output_csv_file="hotel_reviews_raw.csv",
                           min_reviews=200):
    """
    Fetches Google Maps reviews for a given Place ID using SerpAPI and saves them to a CSV file.
    """
    try:
        with open(place_id_file, 'r') as f:
            place_id = f.read().strip()
        if not place_id:
            print(f"Error: Could not read Place ID from {place_id_file}")
            return
        print(f"Using Place ID: {place_id}")
    except FileNotFoundError:
        print(f"Error: Place ID file {place_id_file} not found.")
        return
    except Exception as e:
        print(f"Error reading {place_id_file}: {e}")
        return

    # --- Start of diagnostic code for API key ---
    try:
        with open(api_key_env_file, 'r') as f:
            print(f"Diagnostics: Reading from {api_key_env_file}. Full content scan:")
            line_found_in_direct_read = False
            for i, line_content in enumerate(f):
                print(f"Diagnostics: Line {i+1}: {line_content.strip()}")
                if "SERPAPI_API_KEY" in line_content:
                    print(f"Diagnostics: 'SERPAPI_API_KEY' substring WAS found in line {i+1}.")
                    line_found_in_direct_read = True
            if not line_found_in_direct_read:
                 print(f"Diagnostics: 'SERPAPI_API_KEY' substring was NOT found in any line during direct read.")
    except Exception as e:
        print(f"Diagnostics: Error reading {api_key_env_file} directly: {e}")
    
    load_dotenv(dotenv_path=api_key_env_file, override=True)
    serpapi_api_key = os.getenv("SERPAPI_API_KEY")
    print(f"Attempting to use SerpAPI Key: '{serpapi_api_key}'") # DEBUGGING LINE
    # --- End of diagnostic code for API key ---

    if not serpapi_api_key:
        print(f"Error: SERPAPI_API_KEY not found in {api_key_env_file} or environment.")
        print("Please ensure the API key is correctly set.")
        return

    all_reviews_data = []
    # next_page_token = None # Removed, as client uses 'start'
    reviews_fetched_count = 0
    current_start_index = 0 
    reviews_per_page_assumption = 1 # Changed from 10 to 1

    print(f"Starting to fetch reviews. Aiming for at least {min_reviews} reviews.")
    
    # Initialize the SerpAPI client
    client = serpapi.Client(api_key=serpapi_api_key) # CHANGED api_key_string to api_key

    try:
        page_num = 1
        while reviews_fetched_count < min_reviews:
            print(f"Fetching page {page_num} of reviews (start index: {current_start_index})...")
            params = {
                "engine": "google_maps_reviews",
                "place_id": place_id,
                "hl": "en", # Language
                # "api_key": serpapi_api_key, # Key is now passed to client constructor
                "start": current_start_index 
            }
            # if next_page_token: # Removed next_page_token logic
            #     params["next_page_token"] = next_page_token

            results = client.search(params) 
            
            # The SerpResults object from serpapi-python should act like a dictionary.
            # We will use it directly as actual_results_dict.
            actual_results_dict = results 

            if "error" in actual_results_dict:
                print(f"SerpAPI Error: {actual_results_dict['error']}")
                break 
            
            reviews_on_page = actual_results_dict.get("reviews", [])
            if not reviews_on_page and current_start_index > 0: # If not first page and no reviews, likely end
                print("No more reviews found on this page (after first page).")
                break
            if not reviews_on_page and current_start_index == 0:
                print("No reviews found on the first page.")
                break

            for review in reviews_on_page:
                all_reviews_data.append({
                    "user_name": review.get("user", {}).get("name"),
                    "rating": review.get("rating"),
                    "snippet": review.get("snippet"),
                    "publish_date": review.get("date"),
                    "iso_date": review.get("iso_date"),
                    "likes_count": review.get("likes_count"),
                    "user_link": review.get("user", {}).get("link"),
                    "review_link": review.get("link"),
                    "review_id": review.get("review_id"), 
                    "place_id": place_id
                })
            reviews_fetched_count = len(all_reviews_data)
            print(f"Fetched {len(reviews_on_page)} reviews from page {page_num}. Total reviews so far: {reviews_fetched_count}")

            # Pagination for serpapi.Client() relies on 'start' and checking if reviews_on_page is empty.
            # The check 'if not reviews_on_page and current_start_index > 0:' already handles breaking.
            # The 'len(reviews_on_page) < reviews_per_page_assumption' check will now only be true for 0 reviews.
            
            # Simplified end-of-results check
            if not reviews_on_page: # If any page (after first) returns no reviews, assume end.
                 if page_num > 1: # Only break if it's not the first page and it's empty
                    print("No reviews found on current page, assuming end of data.")
                    break
                 # If first page is empty, the existing check 'if not reviews_on_page and current_start_index == 0:' handles it.

            current_start_index += len(reviews_on_page) 
            # if len(reviews_on_page) == 0 and page_num > 1: # This condition is now covered by the simplified check above
            #     print("No reviews on current page, assuming end of data.")
            #     break
            
            page_num += 1
            
            if reviews_fetched_count >= min_reviews:
                print(f"Reached target of {min_reviews} reviews.")
                break
            
            if page_num > 25: # Adjusted safety break for start index pagination (can be more pages)
                print("Safety break: Fetched 25 pages/attempts of reviews. Stopping.")
                break

        if all_reviews_data:
            df = pd.DataFrame(all_reviews_data)
            df.to_csv(output_csv_file, index=False, encoding='utf-8-sig')
            print(f"Successfully saved {len(df)} reviews to {output_csv_file}")
            if len(df) < min_reviews:
                print(f"Warning: Fetched {len(df)} reviews, which is less than the target of {min_reviews}.")
        else:
            print("No reviews were fetched or extracted.")

    except Exception as e:
        print(f"An error occurred during SerpAPI request or data processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        import dotenv
        import pandas
        import serpapi # Check for the top-level module this time
    except ImportError as e:
        print(f"Missing one or more required libraries (python-dotenv, pandas, serpapi): {e}")
        print("Please ensure they are installed in your venv environment.")
        exit(1)
        
    fetch_reviews_and_save(min_reviews=200) # Ensure min_reviews is 200 when called 