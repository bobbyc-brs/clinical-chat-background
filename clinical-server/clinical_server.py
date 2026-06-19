import json
import os
import time
from typing import Any, Dict, List

from flask import Flask, jsonify, request, send_from_directory
from pydantic import BaseModel, Field
import requests
import yaml

try:
    from pyrpc.RPCServer import RPCServer
    from pyrpc.RPCServerHandler import RPCServerHandler
except Exception:
    RPCServer = None
    RPCServerHandler = object

app = Flask(__name__, static_folder="../web-ui", static_url_path="")
STATE: Dict[str, Any] = {"sessions": {}, "template": None}
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "cohere/north-mini-code:free")

class TranscriptSegment(BaseModel):
    segment_id: int
    start: float
    end: float
    text: str
    confidence: float | None = None

class TranscriptBatch(BaseModel):
    event: str = "transcript_batch"
    session_id: str
    device_id: str
    speaker_role: str
    captured_at: float
    segments: List[TranscriptSegment]

class FieldResult(BaseModel):
    key: str
    value: str | None = None
    confidence: float = 0.0
    evidence: List[str] = Field(default_factory=list)
    status: str = "missing"

class FollowupResult(BaseModel):
    field_key: str
    severity: str
    prompt: str
    reason: str


def load_template():
    with open(os.path.join(os.path.dirname(__file__), "form_template.yaml"), "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)

STATE["template"] = load_template()


def ensure_session(session_id: str):
    if session_id not in STATE["sessions"]:
        fields = {f["key"]: {"key": f["key"], "value": None, "confidence": 0.0, "evidence": [], "status": "missing"} for f in STATE["template"]["fields"]}
        STATE["sessions"][session_id] = {"session_id": session_id, "timeline": [], "fields": fields, "followups": [], "updated_at": time.time()}
    return STATE["sessions"][session_id]


def confidence_status(value: float):
    if value >= 0.85:
        return "filled"
    if value > 0:
        return "review"
    return "missing"


def heuristic_extract(session: Dict[str, Any]):
    template = STATE["template"]["fields"]
    patient_lines = [x for x in session["timeline"] if x["speaker_role"] == "patient"]
    combined = "\n".join(f"{x['speaker_role']}: {x['text']}" for x in session["timeline"])
    for field in template:
        best = None
        terms = [field["label"].lower(), field["key"].lower(), *[s.lower() for s in field.get("synonyms", [])]]
        for item in session["timeline"]:
            txt = item["text"].lower()
            if any(term in txt for term in terms):
                best = item
        if not best and patient_lines:
            if field["key"] in {"chief_complaint", "symptoms", "reason_for_visit"}:
                best = patient_lines[0]
            elif field["key"] in {"duration", "onset", "allergies", "medications", "history", "severity", "red_flags"}:
                best = patient_lines[-1]
        if best:
            conf = float(best.get("confidence") or 0.65)
            session["fields"][field["key"]] = {"key": field["key"], "value": best["text"], "confidence": conf, "evidence": [best["text"]], "status": confidence_status(conf)}
        else:
            session["fields"][field["key"]] = {"key": field["key"], "value": None, "confidence": 0.0, "evidence": [], "status": "missing"}
    followups = []
    for field in template:
        current = session["fields"][field["key"]]
        if current["status"] == "missing" and field.get("prompt_if_missing"):
            followups.append({"field_key": field["key"], "severity": "medium", "prompt": field["prompt_if_missing"], "reason": "missing"})
        elif current["status"] == "review" and field.get("prompt_if_conflict"):
            followups.append({"field_key": field["key"], "severity": "high", "prompt": field["prompt_if_conflict"], "reason": "low_confidence"})
    if any(token in combined.lower() for token in ["maybe", "i think", "not sure"]):
        followups.append({"field_key": "general_uncertainty", "severity": "high", "prompt": "Could you clarify that answer more precisely?", "reason": "uncertain_answer"})
    session["followups"] = followups


def llm_extract(session: Dict[str, Any]):
    if not OPENROUTER_API_KEY:
        heuristic_extract(session)
        return
    schema = {
        "type": "object",
        "properties": {
            "fields": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"},
                        "value": {"type": ["string", "null"]},
                        "confidence": {"type": "number"},
                        "evidence": {"type": "array", "items": {"type": "string"}},
                        "status": {"type": "string"}
                    },
                    "required": ["key", "value", "confidence", "evidence", "status"]
                }
            },
            "followups": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "field_key": {"type": "string"},
                        "severity": {"type": "string"},
                        "prompt": {"type": "string"},
                        "reason": {"type": "string"}
                    },
                    "required": ["field_key", "severity", "prompt", "reason"]
                }
            }
        },
        "required": ["fields", "followups"]
    }
    transcript = "\n".join(f"{x['speaker_role']}: {x['text']} (conf={x.get('confidence')})" for x in session["timeline"])
    field_descriptions = json.dumps(STATE["template"]["fields"], ensure_ascii=False)
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": "Extract configurable medical form fields from the encounter. Use only transcript evidence. Return structured output."},
            {"role": "user", "content": f"Form template: {field_descriptions}\n\nTranscript:\n{transcript}"}
        ],
        "response_format": {"type": "json_schema", "json_schema": {"name": "clinical_form_result", "strict": True, "schema": schema}}
    }
    try:
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}, json=payload, timeout=90)
        resp.raise_for_status()
        body = resp.json()
        content = body["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        for item in parsed.get("fields", []):
            session["fields"][item["key"]] = item
        session["followups"] = parsed.get("followups", [])
    except Exception:
        heuristic_extract(session)


def process_batch(payload: Dict[str, Any]):
    batch = TranscriptBatch(**payload)
    session = ensure_session(batch.session_id)
    for seg in batch.segments:
        session["timeline"].append({
            "segment_id": seg.segment_id,
            "start": seg.start,
            "end": seg.end,
            "text": seg.text,
            "confidence": seg.confidence,
            "speaker_role": batch.speaker_role,
            "device_id": batch.device_id,
        })
    session["timeline"] = sorted(session["timeline"], key=lambda x: (x["start"], x["segment_id"]))
    llm_extract(session)
    session["updated_at"] = time.time()
    return session

class ClinicalRPCHandler(RPCServerHandler):
    def handle_push_transcript(self, payload):
        session = process_batch(payload)
        return {"ok": True, "session_id": session["session_id"], "fields": session["fields"], "followups": session["followups"]}

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "clinical-server-dashboard.html")

@app.route("/api/template")
def get_template():
    return jsonify(STATE["template"])

@app.route("/api/sessions/<session_id>")
def get_session(session_id):
    return jsonify(ensure_session(session_id))

@app.route("/api/ingest", methods=["POST"])
def ingest():
    session = process_batch(request.get_json(force=True))
    return jsonify(session)

@app.route("/api/demo/load", methods=["POST"])
def load_demo():
    doctor = {"event": "transcript_batch", "session_id": "visit-001", "device_id": "doctor-device", "speaker_role": "doctor", "captured_at": time.time(), "segments": [
        {"segment_id": 1, "start": 0.0, "end": 2.0, "text": "What brings you in today?", "confidence": 0.94},
        {"segment_id": 2, "start": 3.0, "end": 5.0, "text": "How long have you had the symptoms?", "confidence": 0.92},
        {"segment_id": 3, "start": 6.0, "end": 8.0, "text": "Do you have any allergies?", "confidence": 0.93}
    ]}
    patient = {"event": "transcript_batch", "session_id": "visit-001", "device_id": "patient-device", "speaker_role": "patient", "captured_at": time.time(), "segments": [
        {"segment_id": 101, "start": 2.1, "end": 2.9, "text": "I have chest tightness and a cough.", "confidence": 0.88},
        {"segment_id": 102, "start": 5.1, "end": 5.9, "text": "For about three days, I think.", "confidence": 0.68},
        {"segment_id": 103, "start": 8.1, "end": 9.0, "text": "Not that I know of.", "confidence": 0.84}
    ]}
    process_batch(doctor)
    session = process_batch(patient)
    return jsonify(session)


def start_rpc_server(host="0.0.0.0", port=9090):
    if RPCServer is None:
        return None
    server = RPCServer((host, port), ClinicalRPCHandler)
    import threading
    th = threading.Thread(target=server.serve_forever, daemon=True)
    th.start()
    return th

if __name__ == "__main__":
    start_rpc_server()
    app.run(host="0.0.0.0", port=8080, debug=False)
