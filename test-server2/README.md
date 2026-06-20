# test-server2 — Headache Protocol Mock Server

A mock clinical server implementing a structured headache intake protocol.
Designed as the backend for the AI-assisted clinical documentation system.

## Files

| File | Purpose |
|---|---|
| `mock_visit_api.py` | Flask mock server — headache protocol scenario |
| `requirements.txt` | Python dependencies |
| `README.md` | This file |

## Install and Run

```bash
pip install -r requirements.txt
python mock_visit_api.py
```

Server starts on `http://localhost:12345`.

## Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Welcome message and endpoint list |
| `/health` | GET | Health check |
| `/api/session` | GET | Current session state (advances scenario each call) |
| `/api/reset` | GET/POST | Reset scenario to tick 0 |
| `/api/state` | GET | Current tick and remaining segments |

## Testing

```bash
# Health check
curl -s http://localhost:12345/health | jq .

# Reset and step through scenario
curl -s http://localhost:12345/api/reset | jq .
curl -s http://localhost:12345/api/session | jq .

# Watch specific fields evolve
curl -s http://localhost:12345/api/session | jq '.fields.neurologic_red_flags'
curl -s http://localhost:12345/api/session | jq '.followups'
curl -s http://localhost:12345/api/session | jq '.metrics'
```

## Scenario

25-segment headache intake covering the standard primary-care headache history protocol:

1. Chief complaint
2. Onset and thunderclap screen
3. Location and character
4. Frequency / duration / severity
5. Associated symptoms (photophobia, phonophobia, aura, nausea)
6. Neurologic and infectious red flags
7. Secondary risk factors (trauma, cancer, pregnancy, anticoagulants, new meds)
8. Triggers and relieving factors
9. Medication use / overuse screening
10. Lifestyle context (sleep, hydration, stress, caffeine)
11. Prior headache history
12. Allergies (ASA / NSAID)
13. Assessment and plan

## Follow-up Logic

Returns top 5 prioritized prompts only (never floods with all missing fields).

Priority order:
1. Low-confidence extracted values — confirm first
2. Asked but not yet answered questions
3. Critical red-flag fields (thunderclap, neurologic, secondary risk)
4. Core diagnostic fields (frequency, associated symptoms, medication use)
5. Contextual / lifestyle fields
6. Optional fields (e.g. air conditioning) — only surface when relevant

## API Contract

Follows the shape defined in `BACKEND_REQUIREMENTS.md`:

```json
{
  "updated_at": 1781910892.16,
  "metrics": {
    "nbFieldsFilled": 5,
    "nbNeedsReview": 2,
    "nbActivePrompts": 5
  },
  "timeline": [...],
  "fields": { "chief_complaint": { "key": "...", "value": "...", "confidence": 0.95, "status": "filled", "evidence": [...] } },
  "followups": [ { "field_key": "...", "severity": "high", "prompt": "...", "reason": "..." } ],
  "screen_areas": { "medical_form": [...], "followup": [...] }
}
```

Field `status` values: `filled` | `review` | `missing`

## Next Steps

- Wire `POST /api/ingest` to receive live transcript batches from edge devices
- Replace hardcoded scenario with LLM-based field extraction (Whisper + Ollama)
- Connect to the browser-based clinical dashboard UI
