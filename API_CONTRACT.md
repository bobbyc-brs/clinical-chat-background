# API Contract

Base URL: `http://localhost:8080`

> **Scope:** Single doctor, single patient, single fixed session. No session management needed.

---

## GET `/api/template`

Returns the medical form definition — the list of fields the LLM fills.

**Request:** none

**Response:**
```json
{
  "form_name": "General Intake Form",
  "fields": [
    {
      "key": "chief_complaint",
      "label": "Chief Complaint",
      "section": "Presenting Problem",
      "synonyms": ["complaint", "problem", "issue", "symptom", "symptoms"],
      "prompt_if_missing": "What is the patient's main complaint today?",
      "prompt_if_conflict": "Can you clarify the main complaint?",
      "position": { "row": 1, "col": 1, "span": 2 }
    }
    // ... more fields
  ]
}
```

**Field shape:**
| Field | Type | Description |
|---|---|---|
| `key` | `string` | Unique field identifier |
| `label` | `string` | Human-readable field name |
| `section` | `string` | Group/section the field belongs to |
| `synonyms` | `string[]` | Alternative words used for detection |
| `prompt_if_missing` | `string` | Follow-up question if field not found |
| `prompt_if_conflict` | `string` | Follow-up question if field is low confidence |
| `position.row` | `number` | Row in the form grid |
| `position.col` | `number` | Column in the form grid (1 or 2) |
| `position.span` | `number?` | If `2`, field spans both columns |

---

## GET `/api/session`

Returns the current state of the session — metrics summary, timeline, extracted fields, and follow-up prompts. Poll this every 3s to drive the entire UI.

**Request:** none

**Response:**
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

**Metrics shape:**
| Field | Type | Description |
|---|---|---|
| `nbFieldsFilled` | `number` | Count of fields with `status === "filled"` |
| `nbNeedsReview` | `number` | Count of fields with `status === "review"` |
| `nbActivePrompts` | `number` | Count of active follow-up prompts (length of `followups[]`) |

**Timeline item shape:**
| Field | Type | Description |
|---|---|---|
| `segment_id` | `number` | Unique segment identifier |
| `start` | `number` | Start time in seconds |
| `end` | `number` | End time in seconds |
| `text` | `string` | Transcribed text |
| `confidence` | `number \| null` | STT confidence score (0–1) |
| `speaker_role` | `"doctor" \| "patient"` | Who said it |
| `device_id` | `string` | Source device identifier |

**Field result shape:**
| Field | Type | Description |
|---|---|---|
| `key` | `string` | Matches a key from `/api/template` |
| `value` | `string \| null` | Extracted value, null if not found |
| `confidence` | `number` | LLM confidence score (0–1) |
| `evidence` | `string[]` | Transcript lines used as evidence |
| `status` | `"filled" \| "review" \| "missing"` | Field completion status. Note: LLM sometimes returns `"complete"` instead of `"filled"` — known bug |

**Follow-up prompt shape:**
| Field | Type | Description |
|---|---|---|
| `field_key` | `string` | Which field triggered the prompt |
| `severity` | `"high" \| "medium" \| "low"` | How urgently the info is needed |
| `prompt` | `string` | The question to ask |
| `reason` | `string` | Why the prompt was generated |

---

## POST `/api/ingest`

The main real-time endpoint. Sends a batch of transcript segments from one speaker and triggers LLM extraction. This is what the edge client (mic device) calls.

**Request body:**
```json
{
  "event": "transcript_batch",
  "device_id": "doctor-device",
  "speaker_role": "doctor",
  "captured_at": 1781910892.16,
  "segments": [
    {
      "segment_id": 1,
      "start": 0.0,
      "end": 2.0,
      "text": "What brings you in today?",
      "confidence": 0.94
    }
  ]
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `event` | `string` | No | Always `"transcript_batch"` |
| `device_id` | `string` | Yes | Source device identifier |
| `speaker_role` | `"doctor" \| "patient"` | Yes | Who is speaking |
| `captured_at` | `number` | Yes | Unix timestamp |
| `segments` | `Segment[]` | Yes | Array of transcript segments |
| `segments[].segment_id` | `number` | Yes | Unique segment ID |
| `segments[].start` | `number` | Yes | Start time in seconds |
| `segments[].end` | `number` | Yes | End time in seconds |
| `segments[].text` | `string` | Yes | Transcribed text |
| `segments[].confidence` | `number \| null` | No | STT confidence score (0–1) |

**Response:** same shape as `GET /api/session`

---

## POST `/api/demo/load`

Loads hardcoded demo conversation and runs LLM extraction. For demo purposes only.

**Request:** none

**Response:** same shape as `GET /api/session`

> **Note:** Has a known race condition — calls LLM twice (once per speaker) before both are in the timeline. Fetch `/api/session` after a short delay or on user action to get the final state.

---

## Notes for React frontend

- On app load, call `GET /api/template` once to get form field definitions (use to render the form layout)
- Poll `GET /api/session` every 3s — one call drives the entire UI:
  - `metrics{}` → summary stats (fields filled, needs review, active prompts)
  - `timeline[]` → conversation column
  - `fields{}` → form auto-fill
  - `followups[]` → follow-up suggestions
- The `fields` object is keyed by field `key` (e.g. `session.fields["chief_complaint"]`), not an array
- `status` values: `"filled"`, `"review"`, `"missing"` — normalize LLM output if it returns `"complete"`
- `metrics` is computed server-side for convenience; frontend should treat it as derived/display-only
