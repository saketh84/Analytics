# AI-Powered DRS Review Analytics Platform

An interactive cricket analytics dashboard for exploring Decision Review System (DRS) review outcomes, team review strategy, umpire decision patterns, pressure overs, and commentary sentiment.

## Features

- Interactive Streamlit dashboard with team, innings, decision, and pressure-over filters
- KPI cards for review count, successful reviews, success rate, and upheld decisions
- Team strategy and umpire overturn-rate summaries
- Pressure-over analysis grouped into overs 1–6, 7–14, and 15–20
- Lightweight rule-based commentary sentiment baseline
- Baseline success-rate estimate for filtered records
- Modular analytics code separated from the UI
- Included synthetic CSV dataset so the app runs immediately

## Important data note

The included `data/drs_reviews.csv` is **synthetic demonstration data**, not official match data. The predictive panel is a baseline summary, not a trained machine-learning model. Replace the CSV with a verified dataset before using the results for research or real-world claims.

## Requirements

- Python 3.10+
- pip

## Run locally

```bash
python -m venv .venv
```

Activate the environment:

**macOS / Linux**
```bash
source .venv/bin/activate
```

**Windows**
```powershell
.venv\\Scripts\\activate
```

Install dependencies and start the dashboard:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The dashboard opens in your browser, usually at `http://localhost:8501`.

## Dataset schema

| Column | Meaning |
|---|---|
| `review_id` | Unique review record |
| `match_id` | Demo match identifier |
| `team`, `opponent` | Reviewing team and opponent |
| `innings`, `over` | Innings and over of the review |
| `umpire` | Demo umpire label |
| `original_decision` | Original on-field decision (`Out` / `Not Out`) |
| `review_result` | Final DRS result (`Upheld` / `Overturned`) |
| `review_success` | Whether the review changed the original decision |
| `decision_changed` | Whether the original decision was overturned |
| `commentary` | Short text used for sentiment analysis |

## Suggested future improvements

1. Replace rule-based sentiment with VADER or a transformer sentiment model.
2. Train and evaluate a classifier only after collecting enough verified labelled examples.
3. Add confidence intervals and minimum-sample warnings to team and umpire metrics.
4. Add match/series/date filters and export-to-CSV functionality.
5. Add data validation and automated tests.
6. Connect a verified ball-by-ball source or a manually curated DRS dataset.

## Project structure

```text
ai_powered_drs_review_analytics/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── drs_reviews.csv
└── src/
    ├── __init__.py
    └── analytics.py
```
