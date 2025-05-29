import os
import json
from dotenv import load_dotenv
from openai import OpenAI

HOTEL_FINAL_JSON = "hotel_final.json"
CRITIQUE_OUTPUT_FILE = "hotel_critique.txt"
MODEL_TO_USE = "gpt-4o"

CRITIC_PROMPT_TEMPLATE = """
You are an expert forecast analyst and critique. You have been provided with a hotel rating forecast in JSON format.
Your task is to critically evaluate this forecast. Please consider the following aspects in your critique:

1.  **Forecast Plausibility:** Is the mean predicted rating (and its standard deviation) plausible for a hotel like the Montreal Marriott Château Champlain in early June? Consider the individual forecast values as well: is the range wide or narrow? Are there any outliers that seem questionable (e.g., the 3.0)?
2.  **Methodology (Implied):** The forecast is an aggregation of predictions from multiple Large Language Models (GPT-4o, Claude 3 Opus, Gemini 1.5 Pro at different temperatures). Comment on the strengths and weaknesses of such an ensemble approach for this specific forecasting task. Does it inherently mitigate bias, or could it amplify certain types of errors?
3.  **Information Basis (Assumed):** The LLMs were provided with a baseline mean rating of 4.12 (from 200 reviews) and recent (sparse) daily review data for April-May 2025 (which included a 1.0 mean rating on one day with 25 reviews, and mostly 5.0s or 4.0s on other active days). Does the final forecast seem to reasonably incorporate this historical context, or does it deviate significantly?
4.  **Potential Biases:** What potential biases could have influenced this forecast? (e.g., model training data biases, recency bias from the daily data, prompt formulation if it inadvertently led models in a certain direction - though you don't have the exact prompt, you can infer some from the context). The prompt aimed for a standard forecast considering baseline, seasonality, and general trends.
5.  **Missing Considerations:** Are there any critical factors that might have been overlooked in generating a hotel rating forecast for early June in Montreal a year in advance? (e.g., specific major city events not discoverable by LLMs without real-time search, impact of unannounced renovations, specific competitor actions).
6.  **Confidence and Actionability:** How much confidence would you place in this forecast? Is the standard deviation useful for decision-making? What caveats should a user be aware of?

Please provide a structured critique addressing these points. Be specific and constructive.

Here is the hotel forecast data:

```json
{forecast_json_content}
```

End your critique with a summary of the top 2-3 most important concerns or limitations.
"""

def main():
    load_dotenv(dotenv_path=".env")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: OPENAI_API_KEY not found in .env file.")
        return

    try:
        with open(HOTEL_FINAL_JSON, 'r') as f:
            hotel_final_data_str = f.read()
            # Validate it's JSON, though we're passing as string in prompt
            json.loads(hotel_final_data_str) 
    except FileNotFoundError:
        print(f"Error: {HOTEL_FINAL_JSON} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {HOTEL_FINAL_JSON}.")
        return

    # Prepare the full prompt
    full_prompt = CRITIC_PROMPT_TEMPLATE.format(forecast_json_content=hotel_final_data_str)

    client = OpenAI(api_key=openai_api_key)
    print(f"Sending critique request to {MODEL_TO_USE} for {HOTEL_FINAL_JSON}...")

    try:
        completion = client.chat.completions.create(
            model=MODEL_TO_USE,
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.3, # Low temp for more focused critique
            max_tokens=1500 # Allow for a detailed critique
        )
        critique_text = completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        return

    try:
        with open(CRITIQUE_OUTPUT_FILE, 'w') as f:
            f.write(critique_text)
        print(f"Critique saved to {CRITIQUE_OUTPUT_FILE}")
    except Exception as e:
        print(f"Error saving critique to {CRITIQUE_OUTPUT_FILE}: {e}")

if __name__ == "__main__":
    main() 