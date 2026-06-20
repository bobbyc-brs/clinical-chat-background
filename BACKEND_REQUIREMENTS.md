# Backend Requirements for React UI

This document describes exactly what the React UI needs from the server. Bobby, please implement these before the UI can go live.

---

## 1. Rename the session endpoint

| Current | Required |
|---|---|
| `GET /api/sessions/:session_id` | `GET /api/session` |

No session ID parameter — single fixed session for this hackathon.

---

## 2. Response shape for `GET /api/session`

```json
{
  "updated_at": 1781910892.16,
  "metrics": {
    "nbFieldsFilled": 3,
    "nbNeedsReview": 1,
    "nbActivePrompts": 2
  },
  "timeline": [
    {
      "segment_id": 1,
      "start": 0.0,
      "end": 2.0,
      "text": "What brings you in today?",
      "confidence": 0.94,
      "speaker_role": "doctor",
      "device_id": "doctor-device"
    }
  ],
  "fields": {
    "chief_complaint": {
      "key": "chief_complaint",
      "value": "chest tightness and a cough",
      "confidence": 0.88,
      "evidence": ["I have chest tightness and a cough."],
      "status": "filled"
    }
  },
  "followups": [
    {
      "field_key": "medications",
      "severity": "high",
      "prompt": "Are you taking any medications right now?",
      "reason": "No medication information provided in transcript."
    }
  ]
}
```

---

## 3. Field-by-field requirements

### `metrics` (new — needs to be added)

Derived counts, cheap to compute server-side:

| Field | Type | How to compute |
|---|---|---|
| `nbFieldsFilled` | `number` | `len([f for f in fields.values() if f["status"] == "filled"])` |
| `nbNeedsReview` | `number` | `len([f for f in fields.values() if f["status"] == "review"])` |
| `nbActivePrompts` | `number` | `len(followups)` |

### `timeline[]`

No changes needed — already correct shape.

### `fields{}`

Must be a **dict keyed by field key**, not an array. Already correct in the current server.

`status` must be one of `"filled"`, `"review"`, `"missing"`. Do **not** return `"complete"` — the UI will not render it correctly.

### `followups[]`

No changes needed — already correct shape.

---

## 4. `POST /api/ingest` — drop `session_id`

The edge client currently sends `session_id` in the request body. This field can be ignored or removed — the server appends to the single fixed session regardless.

---

## 5. CORS

The React UI runs on a different port (Vercel / `localhost:5173`). Please add CORS headers so the browser can call the API:

```python
from flask_cors import CORS
CORS(app)
```

Install: `pip install flask-cors`
