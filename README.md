# INSY 697 Individual Project: Hotel & Trump Forecasts

This project undertakes the task of forecasting two distinct metrics for the period of **June 2-6, 2025**:
1.  The average Google review star rating for the **Montreal Marriott Château Champlain** hotel.
2.  The average daily number of Truth Social posts by **Donald J. Trump**.

The project follows a structured methodology involving several phases:

## Project Phases & Key Activities

1.  **Environment Setup (T01-T05):**
    *   Initialized a Git repository.
    *   Set up a Python 3.11 virtual environment (`venv`).
    *   Installed necessary dependencies (e.g., `openai`, `anthropic`, `google-generativeai`, `pandas`, `python-dotenv`, API-specific SDKs like `google-search-results` for SerpAPI and `apify-client`).
    *   Managed API keys using a `.env` file (for OpenAI, Anthropic, Google AI Studio/Gemini, SerpAPI, Apify).

2.  **Data Acquisition (Phase 1A: Hotel - T10-T14; Phase 1B: Trump - T20-T24):**
    *   **Hotel Reviews:**
        *   Retrieved Google Maps Place ID for the hotel (`hotel_place_id.txt`).
        *   Fetched 200 recent Google reviews via SerpAPI (`hotel_reviews_raw.csv`).
        *   Calculated baseline rating/count (`hotel_baseline.txt`) and daily metrics (`hotel_daily_metrics.csv`).
    *   **Trump Posts:**
        *   Downloaded ~60 days of Truth Social posts via an Apify scraper (`trump_posts_raw.json`).
        *   Parsed to daily counts (`trump_posts_daily.csv`).
        *   Computed baseline stats (`trump_baseline.txt`) and generated a plot (`trump_daily_posts_plot.png`).
    *   All generated data files were committed to Git.

3.  **Prompt Engineering (Phase 2A: Hotel - T30-T35; Phase 2B: Trump - T40-T46):**
    *   Drafted multiple prompt variants (base, Chain-of-Thought, context-aware) for each forecast (`*_prompt_base.txt`, `*_prompt_cot.txt`, etc.).
    *   Back-tested prompts using OpenAI GPT-3.5 against a historical window to select the best-performing prompt based on Mean Absolute Error (MAE). Results in `*_prompt_eval.csv`.
    *   Selected prompts recorded in `prompt_selection.txt`.
    *   Ran ensemble forecasts using the chosen prompt across OpenAI GPT-4o, Anthropic Claude 3 Opus, and Google Gemini 1.5 Pro, each at temperatures 0.2 and 0.7. Raw ensemble predictions are in `*_preds_raw.json`.
    *   Aggregated ensemble predictions to a mean and standard deviation (`*_final.json`).

4.  **Validation & Hallucination Checks (Phase 3 - T50-T52):**
    *   Generated automated critiques of the final forecasts using GPT-4o (`*_critique.txt`).
    *   Revised the hotel forecast based on critique insights (rationale in `hotel_revision_rationale.txt`).

5.  **Report Assembly (Phase 4 - T60-T62):**
    *   Drafted a final `report.md` detailing the methodology, predictions, rationales, limitations, and mitigation strategies.

## Key Output Files

*   Final Forecasts: `hotel_final.json`, `trump_final.json`
*   Detailed Report: `report.md` (and `report.pdf` if generated)
*   Critiques: `hotel_critique.txt`, `trump_critique.txt`
*   Selected Prompts: `hotel_prompt_cot_with_data.txt` (derived from `hotel_prompt_cot.txt`), `trump_prompt_context.txt`
*   Raw Data: `hotel_reviews_raw.csv`, `trump_posts_raw.json`
*   Processed Data: `hotel_daily_metrics.csv`, `trump_posts_daily.csv`, etc.

## Scripts

The project includes various Python scripts to automate these tasks, generally following a `verb_noun.py` naming convention (e.g., `get_hotel_reviews.py`, `calculate_trump_stats.py`, `evaluate_hotel_prompts.py`, `generate_ensemble_forecasts_trump.py`, `critique_hotel_forecast.py`, etc.).

Refer to `insy697_individual_project_tasks.md` for the detailed task list that guided this project. 