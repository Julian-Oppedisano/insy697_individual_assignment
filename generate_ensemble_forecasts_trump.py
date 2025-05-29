import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import google.generativeai as genai

CHOSEN_PROMPT_FILE = "trump_prompt_context.txt" # Using the selected prompt
OUTPUT_JSON_FILE = "trump_preds_raw.json"

MODEL_CONFIG = [
    {"provider": "openai", "model_name": "gpt-4o", "api_key_env": "OPENAI_API_KEY"},
    {"provider": "anthropic", "model_name": "claude-3-opus-20240229", "api_key_env": "ANTHROPIC_API_KEY"},
    {"provider": "google", "model_name": "gemini-1.5-pro-latest", "api_key_env": "GEMINI_API_KEY"}
]
TEMPERATURES = [0.2, 0.7]

def parse_forecast_from_response(response_text):
    """Extracts a numerical forecast (X.X) from the LLM's text response."""
    if not response_text: return None
    match = re.search(r"Final Forecast:\s*([0-9]+(?:\.[0-9]+)?)", response_text, re.IGNORECASE)
    if match:
        try: return round(float(match.group(1)), 1)
        except ValueError: pass
    
    # Fallback for numbers if no prefix, favoring those closer to a plausible post count
    matches = re.findall(r"\b([0-9]+(?:\.[0-9]+)?)\b", response_text)
    if matches:
        for m_str in reversed(matches):
            try:
                val = float(m_str)
                if 0 <= val <= 100: # Trump posts could be higher than hotel ratings, wider range
                    return round(val,1)
            except ValueError:
                continue
    print(f"Warning: Could not extract a valid forecast from response: '{response_text[:100]}...'")
    return None

def get_openai_completion(api_key, model_name, prompt, temperature):
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=700 # Increased slightly for potentially longer reasoning
    )
    return completion.choices[0].message.content.strip()

def get_anthropic_completion(api_key, model_name, prompt, temperature):
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model_name,
        max_tokens=1024,
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
            prompt_content = f.read()
    except FileNotFoundError:
        print(f"Error: Chosen prompt file {CHOSEN_PROMPT_FILE} not found.")
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
            continue

        for temp in TEMPERATURES:
            print(f"\n--- Running: {provider.capitalize()} {model_name} with temp={temp} ---")
            full_response = None
            error_message = None
            extracted_forecast = None

            try:
                if provider == "openai":
                    full_response = get_openai_completion(api_key, model_name, prompt_content, temp)
                elif provider == "anthropic":
                    full_response = get_anthropic_completion(api_key, model_name, prompt_content, temp)
                elif provider == "google":
                    full_response = get_google_completion(api_key, model_name, prompt_content, temp)
                
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
                "prompt_file": CHOSEN_PROMPT_FILE,
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