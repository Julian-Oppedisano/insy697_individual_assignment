

# INSY 697 Individual Project – Atomic Task List

A queue of ultra‑granular, test‑ready tasks for forecasting (1) the Google‑review star rating of **Montreal Marriott Château Champlain** and (2) **Donald J. Trump’s Truth‑Social post frequency** for 2 – 6 June 2025. Execute sequentially; each task has one concern, an explicit start trigger, and a measurable end state.

|ID|Task|Start|End / Test|
|---|---|---|---|
|**Phase 0 – Environment Setup**||||
|T01|Create local folder `insy697_project`|Open terminal|`ls` lists folder|
|T02|Initialise git repo inside the folder|`cd insy697_project`|`git status` OK|
|T03|Create Python 3.11 virtual‑env `venv`|Terminal command|`python -m pip list` shows empty env|
|T04|Install deps: `openai anthropic googlemaps pandas requests`|`pip install`|`pip freeze` lists pkgs|
|T05|Add `.env` with API keys (OpenAI, Anthropic, Google Maps, Factba.se)|Editor opens file|`cat .env` shows keys present|
|**Phase 1 – Data Acquisition (A): Hotel Reviews**||||
|T10|Retrieve Google Maps `place_id` for hotel|Run quick script|`hotel_place_id.txt` saved|
|T11|Pull latest 200 Google reviews via Places API / SerpAPI|Run scraper|`hotel_reviews_raw.csv` exists, ≥200 rows|
|T12|Calculate current mean rating & review count|Run notebook cell|`hotel_baseline.txt` with two numbers|
|T13|Fetch daily new‑review counts & mean rating for last 30 days|Script with API pagination|`hotel_daily_metrics.csv` 30 rows|
|T14|Commit raw & processed hotel data to git|`git add .`|`git log` shows commit|
|**Phase 1 – Data Acquisition (B): Trump Posts**||||
|T20|Download Trump Truth‑Social posts (past 60 days) via Factba.se API|Run fetch script|`trump_posts_raw.json` exists|
|T21|Parse JSON → dataframe (date, post_count)|Notebook cell|`trump_posts_daily.csv` saved|
|T22|Compute 30‑day mean & σ of daily posts|Notebook cell|`trump_baseline.txt` written|
|T23|Visual sanity‑check: line plot of daily counts|Quick matplotlib cell|Plot renders without error|
|T24|Commit Trump datasets & plot|`git add .`|Commit in log|
|**Phase 2 – Prompt Engineering (A): Hotel Forecast**||||
|T30|Draft base prompt `hotel_prompt_base.txt` (no CoT)|Text editor|File saved|
|T31|Draft CoT prompt `hotel_prompt_cot.txt` with step‑by‑step reasoning|Editor|File saved|
|T32|Draft retrieval‑aware prompt `hotel_prompt_scenario.txt` (review‑influx what‑ifs)|Editor|File saved|
|T33|Back‑test each prompt on data window 23 – 27 May (supply true means) using ChatGPT 3.5|Script run|`hotel_prompt_eval.csv` MAE per prompt|
|T34|Select best prompt (lowest MAE) & note ID|Update `prompt_selection.txt`|File contains chosen prompt name|
|T35|Ensemble: run chosen prompt across ChatGPT‑4o, Claude 3, Gemini 1.5, temp = {0.2, 0.7}|Script loop|`hotel_preds_raw.json` 6 predictions|
|T36|Aggregate hotel predictions (mean ± std) → `hotel_final.json`|Notebook cell|JSON contains avg & CI|
|**Phase 2 – Prompt Engineering (B): Trump Forecast**||||
|T40|Draft base prompt `trump_prompt_base.txt`|Editor|File saved|
|T41|Draft CoT prompt `trump_prompt_cot.txt`|Editor|File saved|
|T42|Add calendar context prompt `trump_prompt_context.txt` (no major events)|Editor|File saved|
|T43|Back‑test prompts on window 18 – 22 May using ChatGPT 3.5|Script|`trump_prompt_eval.csv` MAE per prompt|
|T44|Choose best prompt & record in `prompt_selection.txt`|Update file|Trump entry present|
|T45|Ensemble: run best prompt across 3 models × 2 temps|Script|`trump_preds_raw.json` saved|
|T46|Aggregate predictions to daily‑mean & CI → `trump_final.json`|Notebook cell|JSON written|
|**Phase 3 – Validation & Hallucination Checks**||||
|T50|Self‑critique: feed `hotel_final.json` to ChatGPT with "critic" prompt|Run API call|`hotel_critique.txt` saved|
|T51|Self‑critique same for `trump_final.json`|API call|`trump_critique.txt` saved|
|T52|If critiques flag issues, revise forecasts & document rationale|Edit JSONs|`*_final.json` updated, change logged|
|**Phase 4 – Report Assembly & Submission**||||
|T60|Draft Methodology section (≤1 page) in `report.md`|Markdown editor|Section complete|
|T61|Draft Predictions & Rationales section|Editor|Section done|
|T62|Draft Analysis (limitations, hallucination mitigations)|Editor|Section done|
|T63|Convert `report.md` → PDF via `pandoc`|CLI|`report.pdf` exists|
|T64|Verify PDF: 4 pages, 12‑pt Times NR, 1" margins|Open file|Checks pass|
|T65|Rename file `IndividualProject-Firstname-Lastname-ID.pdf`|`mv` command|File renamed correctly|
|T66|Submit on MyCourses & save confirmation screenshot `submission.png`|Browser upload|Screenshot saved + committed|