import os
import json
from dotenv import load_dotenv
from openai import OpenAI

TRUMP_FINAL_JSON = "trump_final.json"
CRITIQUE_OUTPUT_FILE = "trump_critique.txt"
MODEL_TO_USE = "gpt-4o"

CRITIC_PROMPT_TEMPLATE = """
You are an expert forecast analyst and critique, specializing in political communication and social media trends. You have been provided with a forecast for Donald J. Trump's average daily Truth Social post frequency in JSON format.
Your task is to critically evaluate this forecast. Please consider the following aspects in your critique:

1.  **Forecast Plausibility:** The mean predicted daily post count is {mean_posts} with a standard deviation of {std_dev_posts}. The individual forecasts are {individual_forecasts}. Is this overall forecast plausible for Trump in early June 2025, given the specific instruction that the LLMs should assume a period with 'no major pre-scheduled political events, significant anniversaries, major court dates, or national holidays'?
2.  **Methodology (Implied):** The forecast is an aggregation of predictions from multiple Large Language Models (GPT-4o, Claude 3 Opus, Gemini 1.5 Pro at different temperatures) using a prompt that specified a "no major events" context. Comment on this ensemble approach. How might the "no major events" instruction have influenced the LLMs? Did it likely lead to more conservative/stable forecasts? Is the very low standard deviation of the ensemble predictions surprising or expected under this condition?
3.  **Information Basis (Assumed):** The LLMs were provided with baseline statistics from late May 2025 (mean daily posts: 16.31, std dev: 7.84). Does the final forecast ({mean_posts}) simply anchor too heavily on this baseline, especially given the "no major events" context? Or does it reflect a reasonable expectation of continuity?
4.  **Potential Biases:** What potential biases could have influenced this forecast? Consider:
    *   **Anchoring Bias:** Did the models overly rely on the provided baseline?
    *   **Model Training Data:** LLMs' general knowledge of Trump's posting behavior might be extensive. How does this interact with a specific "no major events" instruction for a future period?
    *   **Prompt Interpretation:** Could the "no major events" rule have been interpreted too strictly, suppressing any consideration of typical, minor news-reactive posting?
5.  **Missing Considerations:** Even assuming no *major scheduled* events, Trump's posting can be highly reactive to daily news cycles or spontaneous thoughts. Does the forecast methodology adequately account for this inherent volatility if the period, while lacking major events, is still filled with minor stimuli? Are there other factors related to early June 2025 that might be relevant even without being "major events"?
6.  **Confidence and Actionability:** How much confidence would you place in this forecast of {mean_posts} ± {std_dev_posts}? Is it a useful prediction, or does the "no major events" constraint make it too artificial? What caveats are critical for a user of this forecast?

Please provide a structured critique. Be specific and constructive.

Here is the Trump post forecast data:

```json
{forecast_json_content}
```

End your critique with a summary of the top 2-3 most important concerns or limitations regarding this forecast and its generation process.
"""

def main():
    load_dotenv(dotenv_path=".env")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: OPENAI_API_KEY not found in .env file.")
        return

    try:
        with open(TRUMP_FINAL_JSON, 'r') as f:
            trump_final_data_str = f.read()
            forecast_data = json.loads(trump_final_data_str) # Parse for inserting into prompt
    except FileNotFoundError:
        print(f"Error: {TRUMP_FINAL_JSON} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {TRUMP_FINAL_JSON}.")
        return

    # Prepare the full prompt with details from the JSON
    full_prompt = CRITIC_PROMPT_TEMPLATE.format(
        mean_posts=forecast_data.get("mean_predicted_daily_posts"),
        std_dev_posts=forecast_data.get("std_dev_predicted_daily_posts"),
        individual_forecasts=forecast_data.get("individual_valid_forecasts", []),
        forecast_json_content=trump_final_data_str
    )

    client = OpenAI(api_key=openai_api_key)
    print(f"Sending critique request to {MODEL_TO_USE} for {TRUMP_FINAL_JSON}...")

    try:
        completion = client.chat.completions.create(
            model=MODEL_TO_USE,
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.3, # Low temp for focused critique
            max_tokens=1500 # Allow for detailed critique
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