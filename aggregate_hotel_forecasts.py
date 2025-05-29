import json
import numpy as np

RAW_PREDICTIONS_FILE = "hotel_preds_raw.json"
FINAL_FORECAST_FILE = "hotel_final.json"

def main():
    try:
        with open(RAW_PREDICTIONS_FILE, 'r') as f:
            raw_predictions = json.load(f)
    except FileNotFoundError:
        print(f"Error: Raw predictions file {RAW_PREDICTIONS_FILE} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {RAW_PREDICTIONS_FILE}.")
        return

    valid_forecasts = []
    for pred in raw_predictions:
        if pred.get("extracted_forecast") is not None and pred.get("error_message") is None:
            try:
                forecast_value = float(pred["extracted_forecast"])
                valid_forecasts.append(forecast_value)
            except (ValueError, TypeError):
                print(f"Warning: Could not convert forecast '{pred['extracted_forecast']}' to float for model {pred.get('model_name')}. Skipping.")
        elif pred.get("error_message"):
            print(f"Note: Skipping entry for {pred.get('provider')} {pred.get('model_name')} due to error: {pred.get('error_message')}")

    if not valid_forecasts:
        print("Error: No valid forecasts found to aggregate.")
        # Create an empty/error state for hotel_final.json or handle as per requirements
        final_data = {
            "forecast_period": "June 2, 2025 - June 6, 2025",
            "mean_predicted_rating": None,
            "std_dev_predicted_rating": None,
            "individual_valid_forecasts": [],
            "number_of_valid_forecasts": 0,
            "notes": "No valid individual forecasts were available to calculate an aggregate."
        }
    else:
        mean_forecast = round(np.mean(valid_forecasts), 2) # Rounded to two decimal places
        std_dev_forecast = round(np.std(valid_forecasts), 2) # Rounded to two decimal places
        
        final_data = {
            "forecast_period": "June 2, 2025 - June 6, 2025",
            "mean_predicted_rating": mean_forecast,
            "std_dev_predicted_rating": std_dev_forecast,
            "individual_valid_forecasts": valid_forecasts,
            "number_of_valid_forecasts": len(valid_forecasts),
            "notes": f"Aggregated from {len(valid_forecasts)} forecasts. Check {RAW_PREDICTIONS_FILE} for details on each model's run."
        }
        print(f"\nAggregated Hotel Forecast:")
        print(f"  Mean Predicted Rating: {mean_forecast}")
        print(f"  Std Dev of Predictions: {std_dev_forecast}")
        print(f"  Based on {len(valid_forecasts)} individual forecasts: {valid_forecasts}")

    try:
        with open(FINAL_FORECAST_FILE, 'w') as f:
            json.dump(final_data, f, indent=4)
        print(f"\nFinal aggregated hotel forecast saved to {FINAL_FORECAST_FILE}")
    except Exception as e:
        print(f"Error saving final aggregated forecast to {FINAL_FORECAST_FILE}: {e}")

if __name__ == "__main__":
    main() 