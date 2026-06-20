# Mock Visit API - ASA Allergy and Tylenol Scenario

This package contains an updated front-end testing scenario and API server.

## Files

- `headache-weather-scenario.txt` — scripted doctor-patient conversation
- `mock_visit_api.py` — Flask API server on port 12345
- `evolving-screen-state-sequence.json` — placeholder companion artifact

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install flask
```

## Run

```bash
python mock_visit_api.py
```

Then open or query:

```text
http://localhost:12345/api/sessions/visit-001
```

## Behavior

- Each GET reveals one more 3-second interval.
- The payload includes `metrics`, `timeline`, `fields`, `followups`, and `screen_areas`.
- The scenario now asks about ASA allergy, records a negative response, and recommends Tylenol instead.
- Reset progression with `GET /api/reset`.
