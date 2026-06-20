from flask import Flask, jsonify
from copy import deepcopy
from flask_cors import CORS


app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*","allow_headers": ["Content-Type", "ngrok-skip-browser-warning"]}})

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the TARS Health URL"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

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
    {"segment_id": 21, "start": 60, "end": 63, "speaker_role": "doctor", "device_id": "doctor-device", "text": "Can we check your blood pressure?", "confidence": 0.97},
    {"segment_id": 22, "start": 63, "end": 66, "speaker_role": "patient", "device_id": "patient-device", "text": "Sure.", "confidence": 0.95},
    {"segment_id": 23, "start": 66, "end": 69, "speaker_role": "doctor", "device_id": "doctor-device", "text": "Your blood pressure is fine at 125 over 75.", "confidence": 0.98},
    {"segment_id": 24, "start": 69, "end": 72, "speaker_role": "doctor", "device_id": "doctor-device", "text": "Is anything else bothering you?", "confidence": 0.96},
    {"segment_id": 25, "start": 72, "end": 75, "speaker_role": "patient", "device_id": "patient-device", "text": "The dogs have been waking me up really early, so I have not been sleeping well.", "confidence": 0.87},
    {"segment_id": 26, "start": 75, "end": 78, "speaker_role": "doctor", "device_id": "doctor-device", "text": "Are you allergic to ASAs?", "confidence": 0.97},
    {"segment_id": 27, "start": 78, "end": 81, "speaker_role": "patient", "device_id": "patient-device", "text": "No, I'm not allergic to ASAs.", "confidence": 0.94},
    {"segment_id": 28, "start": 81, "end": 84, "speaker_role": "doctor", "device_id": "doctor-device", "text": "I would suggest Tylenol for headache relief, plus more water and cooling down.", "confidence": 0.95},
    {"segment_id": 29, "start": 84, "end": 87, "speaker_role": "doctor", "device_id": "doctor-device", "text": "I'd like to follow up in 10 days.", "confidence": 0.95},
    {"segment_id": 30, "start": 87, "end": 90, "speaker_role": "doctor", "device_id": "doctor-device", "text": "Do you have air conditioning at home?", "confidence": 0.96},
    {"segment_id": 31, "start": 90, "end": 93, "speaker_role": "patient", "device_id": "patient-device", "text": "No, not in the bedroom.", "confidence": 0.91},
    {"segment_id": 32, "start": 93, "end": 96, "speaker_role": "doctor", "device_id": "doctor-device", "text": "Okay. Heat, dehydration, and poor sleep may all be contributing, so let's work on those.", "confidence": 0.94},
]

FIELD_ORDER = [
    ("chief_complaint", "Chief Complaint"), ("onset", "Onset"), ("frequency", "Frequency"), ("location", "Location"),
    ("severity", "Severity"), ("associated_symptoms", "Associated Symptoms"), ("relieving_factors", "Relieving Factors"),
    ("hydration_context", "Hydration / Heat Context"), ("red_flags", "Red Flags"), ("blood_pressure", "Blood Pressure"),
    ("sleep_disruption", "Sleep Disruption"), ("asa_allergy", "ASA Allergy"), ("treatment_plan", "Treatment Plan"),
    ("followup_interval", "Follow-up Interval"), ("air_conditioning", "Air Conditioning")
]

TICKS = {"value": 0}

def empty_field(label):
    return {"label": label, "value": None, "confidence": 0.0, "status": "missing", "evidence": []}

def build_screen_areas(visible_count):
    allergies = {"label": "Allergies", "value": None, "status": "missing", "confidence": 0.0, "why": "Not answered yet."}
    symptoms = {"label": "Symptoms", "value": None, "status": "missing", "confidence": 0.0, "why": "Chief symptom not described yet."}
    followup_area = []
    if visible_count >= 2:
        symptoms = {"label": "Symptoms", "value": "Headaches since warmer weather.", "status": "review", "confidence": 0.72, "why": "Initial symptom reported, but details still incomplete."}
    if visible_count >= 4:
        symptoms = {"label": "Symptoms", "value": "Headaches since warmer weather, began about two weeks ago.", "status": "review", "confidence": 0.80, "why": "Timing is now known, but pattern and associated symptoms are still incomplete."}
    if visible_count >= 6:
        symptoms = {"label": "Symptoms", "value": "Headaches since warmer weather, began about two weeks ago, almost every afternoon.", "status": "review", "confidence": 0.84, "why": "Frequency is known, but symptom detail is still incomplete."}
    if visible_count >= 8:
        symptoms = {"label": "Symptoms", "value": "Headaches since warmer weather, almost every afternoon, mostly forehead and behind the eyes.", "status": "filled", "confidence": 0.88, "why": "Location is now known and the symptom is usable."}
    if visible_count >= 12:
        symptoms = {"label": "Symptoms", "value": "Headaches since warmer weather, almost every afternoon, forehead and behind the eyes, with mild light sensitivity and no nausea.", "status": "filled", "confidence": 0.91, "why": "Core symptom description is now sufficient to populate the field."}
    if visible_count >= 26:
        allergies = {"label": "Allergies", "value": None, "status": "missing", "confidence": 0.0, "why": "Doctor has asked about ASA allergy, but the patient has not answered yet."}
    if visible_count >= 27:
        allergies = {"label": "Allergies", "value": "No ASA allergy reported.", "status": "filled", "confidence": 0.94, "why": "Patient explicitly denied ASA allergy."}
    if visible_count < 12:
        followup_area.append({"label": "Symptoms detail", "value": "Ask more about symptoms.", "status": "active", "why": "Symptoms are still incomplete."})
    if visible_count < 26:
        followup_area.append({"label": "Allergies", "value": "Ask about ASA allergy.", "status": "active", "why": "ASA allergy has not yet been discussed."})
    elif visible_count == 26:
        followup_area.append({"label": "Allergies", "value": "Await ASA allergy answer.", "status": "active", "why": "Question asked but not yet answered."})
    if visible_count >= 28 and visible_count < 29:
        followup_area.append({"label": "Follow-up", "value": "Plan follow-up timing pending confirmation.", "status": "active", "why": "Treatment discussed; visit follow-up not yet stated."})
    if visible_count >= 29:
        followup_area.append({"label": "Follow-up", "value": "See in 10 days.", "status": "filled", "why": "Doctor explicitly set follow-up timing."})
    if visible_count >= 30 and visible_count < 31:
        followup_area.append({"label": "Air conditioning", "value": "Await answer about air conditioning.", "status": "active", "why": "Doctor asked but patient has not answered yet."})
    if visible_count >= 31:
        followup_area.append({"label": "Air conditioning", "value": "No air conditioning in the bedroom.", "status": "filled", "why": "Patient answered the question."})
    return {"conversation_timeline": "Use timeline[] for the visible doctor/patient utterances.", "medical_form": [allergies, symptoms], "followup": followup_area}

def build_state(tick: int):
    visible_count = min(len(SEGMENTS), tick + 1)
    timeline = deepcopy(SEGMENTS[:visible_count])
    fields = {key: empty_field(label) for key, label in FIELD_ORDER}
    followups = []
    def set_field(key, value, confidence, evidence):
        fields[key]["key"] = key
        fields[key]["value"] = value
        fields[key]["confidence"] = confidence
        fields[key]["status"] = "filled" if confidence >= 0.85 else "review"
        fields[key]["evidence"] = [evidence]
    if visible_count >= 2: set_field("chief_complaint", "Headaches starting with warmer weather", 0.94, SEGMENTS[1]["text"])
    if visible_count >= 4: set_field("onset", "About two weeks ago when hot weather started", 0.90, SEGMENTS[3]["text"])
    if visible_count >= 6: set_field("frequency", "Almost every afternoon", 0.89, SEGMENTS[5]["text"])
    if visible_count >= 8: set_field("location", "Forehead and sometimes behind the eyes", 0.88, SEGMENTS[7]["text"])
    if visible_count >= 10: set_field("severity", "6 / 10", 0.86, SEGMENTS[9]["text"])
    if visible_count >= 12: set_field("associated_symptoms", "Light sensitivity; denies nausea", 0.84, SEGMENTS[11]["text"])
    if visible_count >= 14: set_field("relieving_factors", "Water and rest in a cool room help", 0.90, SEGMENTS[13]["text"])
    if visible_count >= 18: set_field("hydration_context", "More time outside, likely dehydration in heat", 0.82, SEGMENTS[17]["text"])
    if visible_count >= 20: set_field("red_flags", "Denies fever, weakness, or sudden severe headache", 0.91, SEGMENTS[19]["text"])
    if visible_count >= 23: set_field("blood_pressure", "125/75, fine", 0.98, SEGMENTS[22]["text"])
    if visible_count >= 25: set_field("sleep_disruption", "Dogs waking patient early; poor sleep", 0.87, SEGMENTS[24]["text"])
    if visible_count >= 27: set_field("asa_allergy", "No ASA allergy reported", 0.94, SEGMENTS[26]["text"])
    if visible_count >= 28: set_field("treatment_plan", "Suggested Tylenol, hydration, and cooling down", 0.95, SEGMENTS[27]["text"])
    if visible_count >= 29: set_field("followup_interval", "10 days", 0.95, SEGMENTS[28]["text"])
    if visible_count >= 31: set_field("air_conditioning", "No air conditioning in bedroom", 0.91, SEGMENTS[30]["text"])
    for key, field in fields.items():
        field.setdefault("key", key)
        if field["status"] == "missing":
            followups.append({"field_key": key, "severity": "medium", "prompt": f"Ask about {field['label'].lower()}.", "reason": "missing"})
        elif field["status"] == "review":
            followups.append({"field_key": key, "severity": "high", "prompt": f"Confirm {field['label'].lower()}.", "reason": "low_confidence"})
    metrics = {
        "nbActivePrompts": len(followups),
        "nbFieldsFilled": sum(1 for f in fields.values() if f["status"] == "filled"),
        "nbNeedsReview": sum(1 for f in fields.values() if f["status"] == "review"),
    }
    return {
        "updated_at": float(visible_count),
        "metrics": metrics,
        "timeline": timeline,
        "fields": fields,
        "followups": followups,
        "screen_areas": build_screen_areas(visible_count),
    }

@app.route('/api/session')
def session_fixed():
    tick = TICKS['value']
    state = build_state(tick)
    if TICKS['value'] < len(SEGMENTS) - 1:
        TICKS['value'] += 1
    return jsonify(state)

@app.route('/api/reset', methods=['POST', 'GET'])
def reset():
    TICKS['value'] = 0
    return jsonify({"ok": True, "tick": 0})

@app.route('/api/state')
def current_tick():
    return jsonify({"tick": TICKS['value'], "remaining": max(0, len(SEGMENTS) - 1 - TICKS['value'])})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
