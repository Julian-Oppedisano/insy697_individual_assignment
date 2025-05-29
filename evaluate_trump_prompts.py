import os
import json
import re
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

PROMPT_FILES = [
    "trump_prompt_base.txt",
    "trump_prompt_cot.txt",
    "trump_prompt_context.txt"
]
OUTPUT_CSV_FILE = "trump_prompt_eval.csv"
OUTPUT_JSON_DETAILS_FILE = "trump_prompt_eval_details.json"

BACKTEST_START_DATE = "May 18, 2025"
BACKTEST_END_DATE = "May 22, 2025"
BACKTEST_PERIOD_DESCRIPTION = f"{BACKTEST_START_DATE} to {BACKTEST_END_DATE}"

# Ground truth calculated from trump_posts_daily.csv for May 18-22, 2025
# (21+15+9+8+13)/5 = 13.2
GROUND_TRUTH_AVG_POSTS = 13.2

# Baseline stats from trump_baseline.txt (as of May 29)
BASELINE_MEAN = 16.31
BASELINE_STD = 7.84
BASELINE_PERIOD = "May 4, 2025, to May 29, 2025"

MODEL_TO_USE = "gpt-3.5-turbo"

def parse_forecast_from_response(response_text):
    if not response_text: return None
    match = re.search(r"Final Forecast:\s*([0-9]+(?:\.[0-9]+)?)", response_text, re.IGNORECASE)
    if match:
        try: return round(float(match.group(1)), 1)
        except ValueError: pass
    
    # Fallback for numbers if no prefix, favoring those closer to a plausible post count
    # Taking the last number found in typical response structure
    matches = re.findall(r"\b([0-9]+(?:\.[0-9]+)?)\b", response_text)
    if matches:
        for m_str in reversed(matches):
            try:
                val = float(m_str)
                # Heuristic: plausible forecasts are probably 0-50 for daily average
                if 0 <= val <= 50: 
                    return round(val,1)
            except ValueError:
                continue
    print(f"Warning: Could not extract a forecast from response: '{response_text[:100]}...'")
    return None

def modify_prompt_for_backtest(prompt_content):
    # Replace the original forecast period (June 2-6) with the backtest period
    modified_prompt = prompt_content.replace("June 2, 2025, to June 6, 2025", BACKTEST_PERIOD_DESCRIPTION)
    # Ensure baseline info is clearly stated as prior to the backtest period if not already clear
    # The current prompts already use baseline from end of May, which is fine for May 18-22 backtest.
    return modified_prompt

def get_openai_completion(api_key, model_name, prompt, temperature=0.2):
    client = OpenAI(api_key=api_key)
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=500 
        )
        return completion.choices[0].message.content.strip(), None
    except Exception as e:
        print(f"Error calling OpenAI API for {model_name}: {str(e)}")
        return None, str(e)

def main():
    load_dotenv(dotenv_path=".env")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: OPENAI_API_KEY not found in .env file.")
        return

    eval_results = []
    detailed_responses = []

    print(f"Starting Trump prompt evaluation for period: {BACKTEST_PERIOD_DESCRIPTION}")
    print(f"Ground Truth Average Daily Posts: {GROUND_TRUTH_AVG_POSTS}\n")

    for prompt_file in PROMPT_FILES:
        print(f"--- Evaluating: {prompt_file} ---")
        try:
            with open(prompt_file, 'r') as f:
                original_prompt_content = f.read()
        except FileNotFoundError:
            print(f"Error: Prompt file {prompt_file} not found. Skipping.")
            eval_results.append({"prompt_file": prompt_file, "forecast": None, "mae": None, "error": "File not found"})
            detailed_responses.append({"prompt_file": prompt_file, "modified_prompt": None, "raw_response": None, "error": "File not found"})
            continue

        modified_prompt = modify_prompt_for_backtest(original_prompt_content)
        
        raw_response, api_error = get_openai_completion(openai_api_key, MODEL_TO_USE, modified_prompt)
        
        forecast_value = None
        mae = None

        if api_error:
            print(f"  API Error: {api_error}")
        elif raw_response:
            print(f"  Raw response (first 100 chars): {raw_response[:100]}...")
            forecast_value = parse_forecast_from_response(raw_response)
            print(f"  Extracted forecast: {forecast_value}")
            if forecast_value is not None:
                mae = round(abs(forecast_value - GROUND_TRUTH_AVG_POSTS), 2)
                print(f"  MAE: {mae}")
            else:
                print("  Could not parse forecast from response.")
        else:
            print("  No response from API.")

        eval_results.append({
            "prompt_file": prompt_file,
            "forecast": forecast_value,
            "mae": mae,
            "error": api_error
        })
        detailed_responses.append({
            "prompt_file": prompt_file,
            "backtest_period": BACKTEST_PERIOD_DESCRIPTION,
            "ground_truth": GROUND_TRUTH_AVG_POSTS,
            "modified_prompt_sent": modified_prompt,
            "raw_response": raw_response,
            "extracted_forecast": forecast_value,
            "mae": mae,
            "api_error": api_error
        })
        print("---\n")

    # Save to CSV
    df_results = pd.DataFrame(eval_results)
    try:
        df_results.to_csv(OUTPUT_CSV_FILE, index=False)
        print(f"Evaluation results saved to {OUTPUT_CSV_FILE}")
    except Exception as e:
        print(f"Error saving CSV results to {OUTPUT_CSV_FILE}: {e}")

    # Save detailed JSON
    try:
        with open(OUTPUT_JSON_DETAILS_FILE, 'w') as f:
            json.dump(detailed_responses, f, indent=4)
        print(f"Detailed evaluation responses saved to {OUTPUT_JSON_DETAILS_FILE}")
    except Exception as e:
        print(f"Error saving JSON details to {OUTPUT_JSON_DETAILS_FILE}: {e}")

if __name__ == "__main__":
    main() 