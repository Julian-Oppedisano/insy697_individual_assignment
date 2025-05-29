import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import google.generativeai as genai

CHOSEN_PROMPT_FILE = "hotel_prompt_cot.txt"
CHOSEN_PROMPT_FILE_WITH_DATA = "hotel_prompt_cot_with_data.txt"
OUTPUT_JSON_FILE = "hotel_preds_raw.json"

# Define models and their configurations
# For Claude, common models are claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307
# For Gemini, gemini-1.5-pro-latest or gemini-1.0-pro
MODEL_CONFIG = [
    {"provider": "openai", "model_name": "gpt-4o", "api_key_env": "OPENAI_API_KEY"},
    # {"provider": "openai", "model_name": "gpt-3.5-turbo", "api_key_env": "OPENAI_API_KEY"}, # Already used in backtesting
    {"provider": "anthropic", "model_name": "claude-3-opus-20240229", "api_key_env": "ANTHROPIC_API_KEY"},
    {"provider": "google", "model_name": "gemini-1.5-pro-latest", "api_key_env": "GEMINI_API_KEY"}
]
TEMPERATURES = [0.2, 0.7]

def parse_forecast_from_response(response_text):
    """Extracts a numerical forecast (X.X) from the LLM's text response."""
    if not response_text: return None
    # Try to find "Final Forecast: X.X"
    match = re.search(r"Final Forecast:\s*([0-9](?:\.[0-9]+)?)", response_text, re.IGNORECASE)
    if match:
        try: return round(float(match.group(1)), 1) 
        except ValueError: pass
    
    # Fallback: Try to find any number X.X or X (preferring X.X format and 1.0-5.0 range)
    # This regex looks for numbers like 4.2, 3.5, 5.0, or standalone 4, 5
    matches = re.findall(r"(?:\b)([1-5](?:\.[0-9])?|[1-5])(?:\b)", response_text)
    if matches:
        # Prefer numbers that look like typical ratings (e.g., X.X or X.0)
        # Take the last one found as it's often the final answer in a reasoning chain
        for m_str in reversed(matches):
            try:
                val = float(m_str)
                if 1.0 <= val <= 5.0:
                    return round(val, 1) # Ensure one decimal place
            except ValueError:
                continue
    print(f"Warning: Could not extract a valid forecast (1.0-5.0) from response: '{response_text[:100]}...'")
    return None

def get_openai_completion(api_key, model_name, prompt, temperature):
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=300 # Reasonably sized output for forecast + reasoning
    )
    return completion.choices[0].message.content.strip()

def get_anthropic_completion(api_key, model_name, prompt, temperature):
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model_name,
        max_tokens=1024, # Claude can be verbose with reasoning
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()

def get_google_completion(api_key, model_name, prompt, temperature):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(
        prompt, 
        generation_config=genai.types.GenerationConfig(temperature=temperature)
    )
    return response.text.strip()

def main():
    load_dotenv(dotenv_path=".env")
    
    try:
        with open(CHOSEN_PROMPT_FILE, 'r') as f:
            prompt_content_openai = f.read()
    except FileNotFoundError:
        print(f"Error: Chosen prompt file {CHOSEN_PROMPT_FILE} not found.")
        return

    try:
        with open(CHOSEN_PROMPT_FILE_WITH_DATA, 'r') as f:
            prompt_content_anthropic_google = f.read()
    except FileNotFoundError:
        print(f"Error: Chosen prompt file {CHOSEN_PROMPT_FILE_WITH_DATA} not found.")
        return

    all_predictions_data = []
    api_keys = {}
    for cfg in MODEL_CONFIG:
        api_keys[cfg["provider"]] = os.getenv(cfg["api_key_env"])
        if not api_keys[cfg["provider"]]:
            print(f"Warning: API key {cfg['api_key_env']} not found for {cfg['provider']}. Skipping this provider.")

    for config in MODEL_CONFIG:
        provider = config["provider"]
        model_name = config["model_name"]
        api_key = api_keys.get(provider)

        if not api_key:
            continue # Skip if API key wasn't loaded

        for temp in TEMPERATURES:
            print(f"\n--- Running: {provider.capitalize()} {model_name} with temp={temp} ---")
            full_response = None
            error_message = None
            extracted_forecast = None

            # Determine which prompt content to use
            current_prompt_content = prompt_content_openai
            if provider == "anthropic" or provider == "google":
                current_prompt_content = prompt_content_anthropic_google

            try:
                if provider == "openai":
                    full_response = get_openai_completion(api_key, model_name, current_prompt_content, temp)
                elif provider == "anthropic":
                    full_response = get_anthropic_completion(api_key, model_name, current_prompt_content, temp)
                elif provider == "google":
                    full_response = get_google_completion(api_key, model_name, current_prompt_content, temp)
                
                if full_response:
                    print(f"Raw Response (first 300 chars):\n{full_response[:300]}...")
                    extracted_forecast = parse_forecast_from_response(full_response)
                    print(f"Extracted Forecast: {extracted_forecast}")
                else:
                    error_message = "No response from API."
                    print(error_message)

            except Exception as e:
                error_message = f"API Call Error: {str(e)}"
                print(error_message)
            
            all_predictions_data.append({
                "provider": provider,
                "model_name": model_name,
                "temperature": temp,
                "prompt_file": CHOSEN_PROMPT_FILE if provider == "openai" else CHOSEN_PROMPT_FILE_WITH_DATA,
                "raw_response": full_response,
                "extracted_forecast": extracted_forecast,
                "error_message": error_message
            })

    try:
        with open(OUTPUT_JSON_FILE, 'w') as f:
            json.dump(all_predictions_data, f, indent=4)
        print(f"\nEnsemble predictions saved to {OUTPUT_JSON_FILE}")
    except Exception as e:
        print(f"Error saving predictions to {OUTPUT_JSON_FILE}: {e}")

if __name__ == "__main__":
    main() 