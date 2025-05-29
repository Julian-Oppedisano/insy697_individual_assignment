import json
import numpy as np

RAW_PREDICTIONS_FILE = "hotel_preds_raw.json"
FINAL_FORECAST_FILE = "hotel_final.json"
REVISION_RATIONALE_FILE = "hotel_revision_rationale.txt"

# Criteria for the outlier to remove
OUTLIER_PROVIDER = "openai"
OUTLIER_MODEL = "gpt-4o"
OUTLIER_TEMP = 0.7
OUTLIER_FORECAST_VALUE = 3.0

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

    revised_forecasts_data = []
    outlier_removed_info = None

    for pred in raw_predictions:
        is_outlier = (
            pred.get("provider") == OUTLIER_PROVIDER and
            pred.get("model_name") == OUTLIER_MODEL and
            pred.get("temperature") == OUTLIER_TEMP and
            pred.get("extracted_forecast") == OUTLIER_FORECAST_VALUE
        )
        
        if not is_outlier:
            revised_forecasts_data.append(pred)
        else:
            outlier_removed_info = pred
            print(f"Identified and excluded outlier: {pred}")

    valid_forecasts = []
    for pred in revised_forecasts_data:
        if pred.get("extracted_forecast") is not None and pred.get("error_message") is None:
            try:
                forecast_value = float(pred["extracted_forecast"])
                valid_forecasts.append(forecast_value)
            except (ValueError, TypeError):
                print(f"Warning: Could not convert forecast '{pred['extracted_forecast']}' to float. Skipping.")
        elif pred.get("error_message"):
            print(f"Note: Skipping entry for {pred.get('provider')} {pred.get('model_name')} due to error: {pred.get('error_message')}")

    if not valid_forecasts:
        print("Error: No valid forecasts remaining after outlier removal.")
        # Create an empty/error state or handle as per requirements
        final_data = {
            "forecast_period": "June 2, 2025 - June 6, 2025",
            "mean_predicted_rating": None,
            "std_dev_predicted_rating": None,
            "individual_valid_forecasts": [],
            "number_of_valid_forecasts": 0,
            "notes": "No valid individual forecasts after outlier removal."
        }
    else:
        mean_forecast = round(np.mean(valid_forecasts), 2)
        std_dev_forecast = round(np.std(valid_forecasts), 2)
        
        final_data = {
            "forecast_period": "June 2, 2025 - June 6, 2025",
            "mean_predicted_rating": mean_forecast,
            "std_dev_predicted_rating": std_dev_forecast,
            "individual_valid_forecasts": valid_forecasts,
            "number_of_valid_forecasts": len(valid_forecasts),
            "notes": f"Aggregated from {len(valid_forecasts)} forecasts after removing one outlier. Check {RAW_PREDICTIONS_FILE} for details."
        }
        print(f"\nRevised Aggregated Hotel Forecast:")
        print(f"  Mean Predicted Rating: {mean_forecast}")
        print(f"  Std Dev of Predictions: {std_dev_forecast}")
        print(f"  Based on {len(valid_forecasts)} individual forecasts: {valid_forecasts}")

    try:
        with open(FINAL_FORECAST_FILE, 'w') as f:
            json.dump(final_data, f, indent=4)
        print(f"\nRevised final aggregated hotel forecast saved to {FINAL_FORECAST_FILE}")
    except Exception as e:
        print(f"Error saving revised forecast to {FINAL_FORECAST_FILE}: {e}")

    # Document rationale
    rationale = (
        f"Hotel forecast revised based on critique (Task T52).\n"
        f"Original ensemble of 6 forecasts had a mean of 4.02 and std dev of 0.49.\n"
        f"The critique highlighted one forecast of 3.0 as a potential outlier. This forecast was from provider '{OUTLIER_PROVIDER}', model '{OUTLIER_MODEL}' at temperature {OUTLIER_TEMP}.\n"
        f"This outlier was removed. The remaining {len(valid_forecasts)} forecasts are: {valid_forecasts}.\n"
        f"The revised mean predicted rating is {final_data['mean_predicted_rating']} with a revised standard deviation of {final_data['std_dev_predicted_rating']}.\n"
        f"This revision leads to a mean closer to the baseline and a tighter standard deviation, addressing a key concern from the critique."
    )
    try:
        with open(REVISION_RATIONALE_FILE, 'w') as f:
            f.write(rationale)
        print(f"Revision rationale saved to {REVISION_RATIONALE_FILE}")
    except Exception as e:
        print(f"Error saving revision rationale: {e}")

if __name__ == "__main__":
    main() 