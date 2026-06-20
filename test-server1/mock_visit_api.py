from flask import Flask, jsonify
from copy import deepcopy

app = Flask(__name__)

SEGMENTS = [
    {"segment_id": 1, "start": 0, "end": 3, "speaker_role": "doctor", "device_id": "doctor-device", "text": "Hi, what brings you in today?", "confidence": 0.97},
    {"segment_id": 2, "start": 3, "end": 6, "speaker_role": "patient", "device_id": "patient-device", "text": "I've been getting headaches since the weather started getting warmer.", "confidence": 0.94},
    {"segment_id": 3, "start": 6, "end": 9, "speaker_role": "doctor", "device_id": "doctor-device", "text": "When did you first notice them?", "confidence": 0.96},
    {"segment_id": 4, "start": 9, "end": 12, "speaker_role": "patient", "device_id": "patient-device", "text": "About two weeks ago, when the hot days started.", "confidence": 0.90},
    {"segment_id": 5, "start": 12, "end": 15, "speaker_role": "doctor", "device_id": "doctor-device", "text": "How often are you getting the headaches?", "confidence": 0.96},
    {"segment_id": 6, "start": 15, "end": 18, "speaker_role": "patient", "device_id": "patient-device", "text": "Almost every afternoon.", "confidence": 0.89},
    {"segment_id": 7, "start": 18, "end": 21, "speaker_role": "doctor", "device_id": "doctor-device", "text": "Where do you feel the pain?", "confidence": 0.97},
    {"segment_id": 8, "start": 21, "end": 24, "speaker_role": "patient", "device_id": "patient-device", "text": "Mostly across my forehead and sometimes behind my eyes.", "confidence": 0.88},
    {"segment_id": 9, "start": 24, "end": 27, "speaker_role": "doctor", "device_id": "doctor-device", "text": "How severe are they, from zero to ten?", "confidence": 0.97},
    {"segment_id": 10, "start": 27, "end": 30, "speaker_role": "patient", "device_id": "patient-device", "text": "Usually around a six.", "confidence": 0.86},
    {"segment_id": 11, "start": 30, "end": 33, "speaker_role": "doctor", "device_id": "doctor-device", "text": "Any nausea, vision changes, or dizziness?", "confidence": 0.96},
    {"segment_id": 12, "start": 33, "end": 36, "speaker_role": "patient", "device_id": "patient-device", "text": "No nausea, but I do feel a little light-sensitive.", "confidence": 0.84},
    {"segment_id": 13, "start": 36, "end": 39, "speaker_role": "doctor", "device_id": "doctor-device", "text": "Do they get better with water, rest, or medication?", "confidence": 0.95},
    {"segment_id": 14, "start": 39, "end": 42, "speaker_role": "patient", "device_id": "patient-device", "text": "Drinking water and resting in a cool room seems to help.", "confidence": 0.90},
    {"segment_id": 15, "start": 42, "end": 45, "speaker_role": "doctor", "device_id": "doctor-device", "text": "Have you had headaches like this before?", "confidence": 0.95},
    {"segment_id": 16, "start": 45, "end": 48, "speaker_role": "patient", "device_id": "patient-device", "text": "Not this often. Maybe once in a while, but not like this.", "confidence": 0.80},
    {"segment_id": 17, "start": 48, "end": 51, "speaker_role": "doctor", "device_id": "doctor-device", "text": "Are you drinking enough during the day, especially in the heat?", "confidence": 0.96},
    {"segment_id": 18, "start": 51, "end": 54, "speaker_role": "patient", "device_id": "patient-device", "text": "Probably not. I've been outside more and I think I'm getting dehydrated.", "confidence": 0.82},
    {"segment_id": 19, "start": 54, "end": 57, "speaker_role": "doctor", "device_id": "doctor-device", "text": "Any fever, weakness, or sudden severe headache?", "confidence": 0.96},
    {"segment_id": 20, "start": 57, "end": 60, "speaker_role": "patient", "device_id": "patient-device", "text": "No, nothing like that.", "confidence": 0.91},
    {"segment_id": 21, "start": 60, "end": 63, "speaker_role": "doctor", "device_id": "doctor-device", "text": "Okay. We'll note that these seem related to heat and dehydration and talk about prevention.", "confidence": 0.94},
]

FIELD_ORDER = [
    ("chief_complaint", "Chief Complaint"),
    ("onset", "Onset"),
    ("frequency", "Frequency"),
    ("location", "Location"),
    ("severity", "Severity"),
    ("associated_symptoms", "Associated Symptoms"),
    ("relieving_factors", "Relieving Factors"),
    ("hydration_context", "Hydration / Heat Context"),
    ("red_flags", "Red Flags"),
]

TICKS = {"value": 0}

def empty_field(label):
    return {"label": label, "value": None, "confidence": 0.0, "status": "missing", "evidence": []}

def build_state(tick: int):
    visible_count = min(len(SEGMENTS), tick + 1)
    timeline = deepcopy(SEGMENTS[:visible_count])
    fields = {key: empty_field(label) for key, label in FIELD_ORDER}
    followups = []

    def set_field(key, value, confidence, evidence):
        fields[key]["value"] = value
        fields[key]["confidence"] = confidence
        fields[key]["status"] = "filled" if confidence >= 0.85 else "review"
        fields[key]["evidence"] = [evidence]

    if visible_count >= 2:
        set_field("chief_complaint", "Headaches starting with warmer weather", 0.94, SEGMENTS[1]["text"])
    if visible_count >= 4:
        set_field("onset", "About two weeks ago when hot weather started", 0.90, SEGMENTS[3]["text"])
    if visible_count >= 6:
        set_field("frequency", "Almost every afternoon", 0.89, SEGMENTS[5]["text"])
    if visible_count >= 8:
        set_field("location", "Forehead and sometimes behind the eyes", 0.88, SEGMENTS[7]["text"])
    if visible_count >= 10:
        set_field("severity", "6 / 10", 0.86, SEGMENTS[9]["text"])
    if visible_count >= 12:
        set_field("associated_symptoms", "Light sensitivity; denies nausea", 0.84, SEGMENTS[11]["text"])
    if visible_count >= 14:
        set_field("relieving_factors", "Water and rest in a cool room help", 0.90, SEGMENTS[13]["text"])
    if visible_count >= 18:
        set_field("hydration_context", "More time outside, likely dehydration in heat", 0.82, SEGMENTS[17]["text"])
    if visible_count >= 20:
        set_field("red_flags", "Denies fever, weakness, or sudden severe headache", 0.91, SEGMENTS[19]["text"])

    for key, field in fields.items():
        if field["status"] == "missing":
            followups.append({"field_key": key, "severity": "medium", "prompt": f"Ask about {field['label'].lower()}.", "reason": "missing"})
        elif field["status"] == "review":
            followups.append({"field_key": key, "severity": "high", "prompt": f"Confirm {field['label'].lower()}.", "reason": "low_confidence"})

    metrics = {
        "nbActivePrompts": len(followups),
        "nbFieldsFilled": sum(1 for f in fields.values() if f["status"] != "missing"),
        "nbNeedsReview": sum(1 for f in fields.values() if f["status"] == "review"),
        "nbTimelineEntries": len(timeline),
    }

    return {
        "session_id": "visit-001",
        "tick": tick,
        "metrics": metrics,
        "timeline": timeline,
        "fields": fields,
        "followups": followups,
    }

@app.route('/api/sessions/visit-001')
def session_visit_001():
    tick = TICKS["value"]
    state = build_state(tick)
    if TICKS["value"] < len(SEGMENTS) - 1:
        TICKS["value"] += 1
    return jsonify(state)

@app.route('/api/reset', methods=['POST', 'GET'])
def reset():
    TICKS["value"] = 0
    return jsonify({"ok": True, "tick": 0})

@app.route('/api/state')
def current_tick():
    return jsonify({"tick": TICKS["value"], "remaining": max(0, len(SEGMENTS) - 1 - TICKS["value"])})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12345, debug=True)
