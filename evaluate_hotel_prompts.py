import os
import pandas as pd
from datetime import datetime, timedelta
import re
import json
from openai import OpenAI # Ensure openai library is available
from dotenv import load_dotenv

# --- Configuration ---
BACKTEST_DATE_STR = "2025-05-07"
RAW_REVIEWS_FILE = "hotel_reviews_raw.csv"
PROMPT_FILES = {
    "base": "hotel_prompt_base.txt",
    "cot": "hotel_prompt_cot.txt",
    "scenario": "hotel_prompt_scenario.txt"
}
OUTPUT_CSV_FILE = "hotel_prompt_eval.csv"
OPENAI_MODEL = "gpt-3.5-turbo"

# --- Helper Functions ---

def calculate_ground_truth_rating(reviews_file, target_date_str):
    """Calculates the actual mean rating from the reviews file for the given single date."""
    try:
        df = pd.read_csv(reviews_file)
        if 'iso_date' not in df.columns or 'rating' not in df.columns:
            print("Error: 'iso_date' or 'rating' column missing in reviews file.")
            return None
        
        df['iso_date_dt'] = pd.to_datetime(df['iso_date']).dt.date # Convert to date objects
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        
        mask = (df['iso_date_dt'] == target_date)
        filtered_reviews = df.loc[mask]
        
        if filtered_reviews.empty:
            print(f"No reviews found for the date {target_date_str}.")
            return None 
            
        mean_rating = filtered_reviews['rating'].mean()
        print(f"Ground truth for {target_date_str}: {mean_rating:.2f} from {len(filtered_reviews)} reviews.")
        return round(mean_rating, 2)
    except FileNotFoundError:
        print(f"Error: Reviews file {reviews_file} not found.")
        return None
    except Exception as e:
        print(f"Error calculating ground truth: {e}")
        return None

def get_llm_forecast(api_key, prompt_content, model_name):
    """Gets a forecast from the LLM using the provided prompt."""
    try:
        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful forecasting assistant."},
                {"role": "user", "content": prompt_content}
            ],
            temperature=0.7 # As per T35, but we can make this configurable if needed for backtesting
        )
        response_text = completion.choices[0].message.content.strip()
        print(f"LLM Raw Response ({model_name}):\n{response_text}\n------------------")
        
        forecast_val = None
        match = re.search(r"Final Forecast:\s*([0-9](?:\.[0-9]+)?)", response_text, re.IGNORECASE)
        if match:
            forecast_val = float(match.group(1))
        else:
            matches = re.findall(r"(?:^|\s)([0-9](?:\.[0-9]+)?)(?:$|\s)", response_text)
            if matches:
                # Try to be a bit smarter: if multiple numbers, prefer one that looks like a rating (e.g. X.X)
                potential_ratings = [float(m) for m in matches if re.match(r"^[1-5](\.[0-9])?$", m)]
                if potential_ratings:
                    forecast_val = potential_ratings[-1] # take the last valid rating format
                else:
                    forecast_val = float(matches[-1]) # take the last number found if no rating format matches
        
        if forecast_val is not None and 1.0 <= forecast_val <= 5.0:
            return round(forecast_val, 1) # Round to one decimal place as per prompt spec
        else:
            print(f"Warning: Could not extract a valid forecast (1.0-5.0) from LLM response: '{response_text[:100]}...'")
            if forecast_val is not None: print(f"(Extracted value {forecast_val} was out of range)")
            return None

    except Exception as e:
        print(f"Error calling OpenAI API or parsing response: {e}")
        return None

# --- Main Script Logic ---
def main():
    load_dotenv(dotenv_path=".env")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: OPENAI_API_KEY not found in .env file. Cannot proceed.")
        return

    print(f"Backtesting for date: {BACKTEST_DATE_STR}")
    ground_truth_rating = calculate_ground_truth_rating(RAW_REVIEWS_FILE, BACKTEST_DATE_STR)

    if ground_truth_rating is None:
        print("Could not determine ground truth rating. Aborting backtest.")
        return

    results = []

    for prompt_key, prompt_file_path in PROMPT_FILES.items():
        print(f"\n--- Evaluating prompt: {prompt_key} ({prompt_file_path}) ---")
        try:
            with open(prompt_file_path, 'r') as f:
                original_prompt_content = f.read()
            
            # Modify prompt for backtesting: change forecast period to the single backtest date
            # Original target phrase: "for the period of June 2, 2025, to June 6, 2025"
            # New target phrase: "for May 7, 2025"
            backtest_date_obj = datetime.strptime(BACKTEST_DATE_STR, '%Y-%m-%d')
            backtest_period_str_long = f"for {backtest_date_obj.strftime('%B %d, %Y')}" # e.g., "for May 07, 2025"
            backtest_period_str_short = f"for {backtest_date_obj.strftime('%b %d, %Y')}" # e.g., "for May 07, 2025"
            
            modified_prompt = original_prompt_content.replace(
                "for the period of June 2, 2025, to June 6, 2025", 
                backtest_period_str_long
            )
            modified_prompt = modified_prompt.replace(
                "for the period June 2-6, 2025", # A common variant from task list
                backtest_period_str_long
            )
            # A more general replacement for any remaining June 2-6, 2025 phrasing
            modified_prompt = re.sub(
                r"(for (the period (of )?)?)?June\s+2(?:nd|th)?(?:\s*to(?:\s*and)?\s*|\s*-\s*)June\s+6(?:th)?,\s*2025",
                backtest_period_str_long,
                modified_prompt,
                flags=re.IGNORECASE
            )
            # For the scenario prompt, the phrasing might be different for the final forecast part
            modified_prompt = re.sub(
                r"for the period June 2-6, 2025, assuming none",
                f"{backtest_period_str_long}, assuming none",
                modified_prompt,
                flags=re.IGNORECASE
            )

            print(f"Modified prompt for backtest (targeting {backtest_period_str_long}):\n{modified_prompt[:400]}...\n------------------")
            
            llm_forecast = get_llm_forecast(openai_api_key, modified_prompt, OPENAI_MODEL)
            
            mae = None
            if llm_forecast is not None:
                mae = abs(llm_forecast - ground_truth_rating)
                print(f"LLM Forecast for {prompt_key}: {llm_forecast}, Ground Truth: {ground_truth_rating}, MAE: {mae:.2f}")
            else:
                print(f"LLM forecast for {prompt_key} could not be determined.")

            results.append({
                "prompt_name": prompt_key,
                "prompt_file": prompt_file_path,
                "backtest_target_period": BACKTEST_DATE_STR,
                "ground_truth_rating": ground_truth_rating,
                "llm_forecast": llm_forecast,
                "mae": mae if mae is not None else 'Error'
            })

        except FileNotFoundError:
            print(f"Error: Prompt file {prompt_file_path} not found.")
            results.append({
                "prompt_name": prompt_key,
                "prompt_file": prompt_file_path,
                "backtest_target_period": BACKTEST_DATE_STR,
                "ground_truth_rating": ground_truth_rating,
                "llm_forecast": "Error - prompt file not found",
                "mae": "Error"
            })
        except Exception as e_prompt:
            print(f"Error processing prompt {prompt_key}: {e_prompt}")
            results.append({
                "prompt_name": prompt_key,
                "prompt_file": prompt_file_path,
                "backtest_target_period": BACKTEST_DATE_STR,
                "ground_truth_rating": ground_truth_rating,
                "llm_forecast": f"Error - {e_prompt}",
                "mae": "Error"
            })

    # Save results to CSV
    results_df = pd.DataFrame(results)
    try:
        results_df.to_csv(OUTPUT_CSV_FILE, index=False)
        print(f"\nBacktesting results saved to {OUTPUT_CSV_FILE}")
    except Exception as e_csv:
        print(f"Error saving results to CSV {OUTPUT_CSV_FILE}: {e_csv}")

if __name__ == "__main__":
    main() 