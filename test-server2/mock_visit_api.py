"""
test-server2/mock_visit_api.py
Headache protocol mock server — follow-up questions are driven entirely
by what has been said so far, not pre-loaded from the scenario type.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from copy import deepcopy

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": ["Content-Type", "ngrok-skip-browser-warning"]}})

app_state = {"tick": 0}

# ---------------------------------------------------------------------------
# Scenario transcript
# ---------------------------------------------------------------------------
SEGMENTS = [
    {"segment_id": 1,  "start": 0.0,  "end": 3.5,  "text": "Hi, what brings you in today?",                                                                          "confidence": 0.98, "speaker_role": "doctor",  "device_id": "doctor-device"},
    {"segment_id": 2,  "start": 3.5,  "end": 8.5,  "text": "I've had headaches for the past three weeks, and they seem to be getting worse.",                        "confidence": 0.95, "speaker_role": "patient", "device_id": "patient-device"},
    {"segment_id": 3,  "start": 8.5,  "end": 12.0, "text": "When did this headache first start, and did it come on suddenly or gradually?",                           "confidence": 0.97, "speaker_role": "doctor",  "device_id": "doctor-device"},
    {"segment_id": 4,  "start": 12.0, "end": 16.5, "text": "It started gradually about three weeks ago. It's not the worst headache of my life.",                    "confidence": 0.94, "speaker_role": "patient", "device_id": "patient-device"},
    {"segment_id": 5,  "start": 16.5, "end": 20.0, "text": "Where is the pain, and what does it feel like?",                                                          "confidence": 0.97, "speaker_role": "doctor",  "device_id": "doctor-device"},
    {"segment_id": 6,  "start": 20.0, "end": 25.0, "text": "Mostly on both sides of my forehead with a pressure feeling, sometimes throbbing by the afternoon.",     "confidence": 0.92, "speaker_role": "patient", "device_id": "patient-device"},
    {"segment_id": 7,  "start": 25.0, "end": 29.0, "text": "How often are you getting them, how long do they last, and how severe are they out of ten?",              "confidence": 0.97, "speaker_role": "doctor",  "device_id": "doctor-device"},
    {"segment_id": 8,  "start": 29.0, "end": 35.5, "text": "Almost every day, usually for several hours, and around a six or seven out of ten.",                     "confidence": 0.91, "speaker_role": "patient", "device_id": "patient-device"},
    {"segment_id": 9,  "start": 35.5, "end": 40.0, "text": "Any nausea, vomiting, light sensitivity, sound sensitivity, or visual aura?",                            "confidence": 0.96, "speaker_role": "doctor",  "device_id": "doctor-device"},
    {"segment_id": 10, "start": 40.0, "end": 46.5, "text": "I do get light sensitivity and sometimes I want the room quiet, but no vomiting and no visual aura.",    "confidence": 0.89, "speaker_role": "patient", "device_id": "patient-device"},
    {"segment_id": 11, "start": 46.5, "end": 50.5, "text": "Do you have fever, neck stiffness, weakness, numbness, confusion, or trouble speaking?",                  "confidence": 0.97, "speaker_role": "doctor",  "device_id": "doctor-device"},
    {"segment_id": 12, "start": 50.5, "end": 55.5, "text": "No fever, no neck stiffness, and I haven't had weakness or trouble speaking.",                            "confidence": 0.93, "speaker_role": "patient", "device_id": "patient-device"},
    {"segment_id": 13, "start": 55.5, "end": 60.0, "text": "Any recent head injury, cancer history, immune problems, pregnancy, blood thinners, or new medications?", "confidence": 0.96, "speaker_role": "doctor",  "device_id": "doctor-device"},
    {"segment_id": 14, "start": 60.0, "end": 66.5, "text": "No head injury, no cancer, I'm not pregnant, not on blood thinners. I did start a decongestant recently.","confidence": 0.87, "speaker_role": "patient", "device_id": "patient-device"},
    {"segment_id": 15, "start": 66.5, "end": 70.5, "text": "What tends to trigger it, and what makes it better or worse?",                                            "confidence": 0.97, "speaker_role": "doctor",  "device_id": "doctor-device"},
    {"segment_id": 16, "start": 70.5, "end": 77.0, "text": "It gets worse after long screen time and when I skip water. Rest, coffee, and ibuprofen help a bit.",     "confidence": 0.90, "speaker_role": "patient", "device_id": "patient-device"},
    {"segment_id": 17, "start": 77.0, "end": 81.5, "text": "How often are you taking ibuprofen or any other pain medication for this?",                               "confidence": 0.96, "speaker_role": "doctor",  "device_id": "doctor-device"},
    {"segment_id": 18, "start": 81.5, "end": 86.5, "text": "Most days lately, probably five or six days a week.",                                                     "confidence": 0.86, "speaker_role": "patient", "device_id": "patient-device"},
    {"segment_id": 19, "start": 86.5, "end": 90.5, "text": "How have sleep, stress, hydration, and caffeine been recently?",                                          "confidence": 0.97, "speaker_role": "doctor",  "device_id": "doctor-device"},
    {"segment_id": 20, "start": 90.5, "end": 97.0, "text": "Sleep has been poor, work is stressful, I probably don't drink enough water, and I have two large coffees a day.", "confidence": 0.91, "speaker_role": "patient", "device_id": "patient-device"},
    {"segment_id": 21, "start": 97.0, "end": 101.0,"text": "Have you had headaches like this before, or is this a new pattern for you?",                              "confidence": 0.97, "speaker_role": "doctor",  "device_id": "doctor-device"},
    {"segment_id": 22, "start": 101.0,"end": 105.5, "text": "I've had occasional headaches before, but this pattern of near-daily headaches is new.",                 "confidence": 0.92, "speaker_role": "patient", "device_id": "patient-device"},
    {"segment_id": 23, "start": 105.5,"end": 109.5, "text": "Are you allergic to aspirin or any NSAIDs?",                                                              "confidence": 0.97, "speaker_role": "doctor",  "device_id": "doctor-device"},
    {"segment_id": 24, "start": 109.5,"end": 113.5, "text": "No, I am not allergic to aspirin or NSAIDs.",                                                             "confidence": 0.95, "speaker_role": "patient", "device_id": "patient-device"},
    {"segment_id": 25, "start": 113.5,"end": 120.0, "text": "This sounds most consistent with a primary headache. Reduce frequent ibuprofen, hydrate, improve sleep, and keep a headache diary.", "confidence": 0.93, "speaker_role": "doctor", "device_id": "doctor-device"},
]

# ---------------------------------------------------------------------------
# Field catalogue  (key, label, required)
# Fields are LOCKED until the conversation unlocks them.
# ---------------------------------------------------------------------------
ALL_FIELDS = [
    ("chief_complaint",           "Chief Complaint",                    True),
    ("onset_pattern",             "Onset Pattern",                      True),
    ("thunderclap_screen",        "Sudden / Worst Headache Screen",     True),
    ("location_character",        "Location and Character",             True),
    ("frequency_duration_severity","Frequency / Duration / Severity",   True),
    ("associated_symptoms",       "Associated Symptoms",                True),
    ("neurologic_red_flags",      "Neurologic / Infectious Red Flags",  True),
    ("secondary_risk_factors",    "Secondary Risk Factors",             True),
    ("triggers_relief",           "Triggers and Relief",                True),
    ("medication_use",            "Medication Use",                     True),
    ("lifestyle_context",         "Lifestyle Context",                  True),
    ("prior_headache_history",    "Prior Headache History",             True),
    ("allergies",                 "Allergies",                          True),
    ("assessment_plan",           "Assessment and Plan",                True),
    # optional — only unlocked when context appears in conversation
    ("air_conditioning",          "Air Conditioning / Heat Exposure",   False),
]

def new_field(key, label, required):
    return {
        "key": key, "label": label, "value": None,
        "confidence": 0.0, "evidence": [], "status": "missing",
        "asked": False, "answered": False,
        "unlocked": required,   # required fields start unlocked; optional start locked
        "optional": not required,
    }

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def set_field(fields, key, value, confidence, evidence, asked=True, answered=True):
    f = fields[key]
    f["value"]      = value
    f["confidence"] = confidence
    f["evidence"]   = [evidence] if isinstance(evidence, str) else evidence
    f["status"]     = "filled" if confidence >= 0.88 else "review"
    f["asked"]      = asked
    f["answered"]   = answered
    f["unlocked"]   = True

def mark_asked(fields, key):
    fields[key]["asked"]    = True
    fields[key]["unlocked"] = True

# ---------------------------------------------------------------------------
# Unlock optional fields based on conversation content
# ---------------------------------------------------------------------------
HEAT_KEYWORDS = ["heat", "hot", "warm", "outside", "sun", "temperature",
                 "summer", "air conditioning", "ac ", "a/c", "sweat", "cooling"]

def unlock_optional(fields, timeline):
    combined = " ".join(s["text"].lower() for s in timeline)
    if any(kw in combined for kw in HEAT_KEYWORDS):
        fields["air_conditioning"]["unlocked"] = True

# ---------------------------------------------------------------------------
# Build fields state from visible transcript
# ---------------------------------------------------------------------------
def build_fields(visible_count):
    fields = {key: new_field(key, label, req) for key, label, req in ALL_FIELDS}

    # Before segment 2 (patient hasn't spoken yet): nothing to fill
    if visible_count < 2:
        return fields

    # Segment 2 — patient mentions headaches: chief_complaint filled, headache fields unlock
    if visible_count >= 2:
        set_field(fields, "chief_complaint",
                  "Headaches for three weeks, worsening",
                  0.95, SEGMENTS[1]["text"])

    # Segment 3 — doctor asks onset + thunderclap
    if visible_count >= 3:
        mark_asked(fields, "onset_pattern")
        mark_asked(fields, "thunderclap_screen")

    # Segment 4 — patient answers
    if visible_count >= 4:
        set_field(fields, "onset_pattern",
                  "Gradual onset about three weeks ago",
                  0.94, SEGMENTS[3]["text"])
        set_field(fields, "thunderclap_screen",
                  "Not sudden; not the worst headache of life",
                  0.94, SEGMENTS[3]["text"])

    if visible_count >= 5:
        mark_asked(fields, "location_character")
    if visible_count >= 6:
        set_field(fields, "location_character",
                  "Bifrontal pressure, sometimes throbbing in the afternoon",
                  0.92, SEGMENTS[5]["text"])

    if visible_count >= 7:
        mark_asked(fields, "frequency_duration_severity")
    if visible_count >= 8:
        set_field(fields, "frequency_duration_severity",
                  "Near-daily, several hours, 6–7 / 10",
                  0.91, SEGMENTS[7]["text"])

    if visible_count >= 9:
        mark_asked(fields, "associated_symptoms")
    if visible_count >= 10:
        set_field(fields, "associated_symptoms",
                  "Photophobia and phonophobia; no vomiting; no aura",
                  0.89, SEGMENTS[9]["text"])

    if visible_count >= 11:
        mark_asked(fields, "neurologic_red_flags")
    if visible_count >= 12:
        set_field(fields, "neurologic_red_flags",
                  "Denies fever, neck stiffness, weakness, and speech difficulty",
                  0.93, SEGMENTS[11]["text"])

    if visible_count >= 13:
        mark_asked(fields, "secondary_risk_factors")
    if visible_count >= 14:
        set_field(fields, "secondary_risk_factors",
                  "No trauma, cancer, pregnancy, or anticoagulants; new decongestant noted",
                  0.87, SEGMENTS[13]["text"])

    if visible_count >= 15:
        mark_asked(fields, "triggers_relief")
    if visible_count >= 16:
        set_field(fields, "triggers_relief",
                  "Worse with screen time and dehydration; better with rest, coffee, and ibuprofen",
                  0.90, SEGMENTS[15]["text"])

    if visible_count >= 17:
        mark_asked(fields, "medication_use")
    if visible_count >= 18:
        set_field(fields, "medication_use",
                  "Ibuprofen used about 5–6 days per week",
                  0.86, SEGMENTS[17]["text"])

    if visible_count >= 19:
        mark_asked(fields, "lifestyle_context")
    if visible_count >= 20:
        set_field(fields, "lifestyle_context",
                  "Poor sleep, high stress, low hydration, two large coffees daily",
                  0.91, SEGMENTS[19]["text"])

    if visible_count >= 21:
        mark_asked(fields, "prior_headache_history")
    if visible_count >= 22:
        set_field(fields, "prior_headache_history",
                  "Occasional prior headaches; near-daily pattern is new",
                  0.92, SEGMENTS[21]["text"])

    if visible_count >= 23:
        mark_asked(fields, "allergies")
    if visible_count >= 24:
        set_field(fields, "allergies",
                  "No aspirin or NSAID allergy reported",
                  0.95, SEGMENTS[23]["text"])

    if visible_count >= 25:
        set_field(fields, "assessment_plan",
                  "Primary headache pattern; reduce ibuprofen, hydrate, improve sleep, headache diary",
                  0.93, SEGMENTS[24]["text"])

    return fields

# ---------------------------------------------------------------------------
# Priority scoring — only score UNLOCKED fields
# ---------------------------------------------------------------------------
PRIORITIES = {
    "thunderclap_screen":         95,
    "neurologic_red_flags":       92,
    "secondary_risk_factors":     88,
    "frequency_duration_severity":85,
    "associated_symptoms":        82,
    "medication_use":             80,
    "triggers_relief":            76,
    "lifestyle_context":          72,
    "prior_headache_history":     68,
    "location_character":         66,
    "allergies":                  62,
    "onset_pattern":              60,
    "assessment_plan":            50,
    "air_conditioning":           30,
    "chief_complaint":            25,
}

def score(fields, key):
    f = fields[key]
    if not f["unlocked"]:
        return 0
    if f["status"] == "review":
        return 100
    if f["asked"] and not f["answered"]:
        return 98
    if f["status"] == "filled":
        return 0
    return PRIORITIES.get(key, 40)

# ---------------------------------------------------------------------------
# Prompt catalogue
# ---------------------------------------------------------------------------
PROMPTS = {
    "chief_complaint":            ("medium",   "What is the main concern today?"),
    "onset_pattern":              ("high",     "When did the headache start, and was the onset sudden or gradual?"),
    "thunderclap_screen":         ("critical", "Was it sudden, instantly maximal, or the worst headache of your life?"),
    "location_character":         ("medium",   "Where is the pain, and is it pressure, throbbing, or stabbing?"),
    "frequency_duration_severity":("high",     "How often does it happen, how long does it last, and how severe out of ten?"),
    "associated_symptoms":        ("high",     "Any nausea, vomiting, light or sound sensitivity, or visual aura?"),
    "neurologic_red_flags":       ("critical", "Any fever, neck stiffness, weakness, numbness, confusion, or trouble speaking?"),
    "secondary_risk_factors":     ("high",     "Any recent trauma, cancer, immune issues, pregnancy, blood thinners, or new medications?"),
    "triggers_relief":            ("medium",   "What tends to trigger the headache, and what makes it better or worse?"),
    "medication_use":             ("high",     "How often are pain medicines like ibuprofen or acetaminophen being used?"),
    "lifestyle_context":          ("medium",   "How have sleep, stress, hydration, and caffeine been recently?"),
    "prior_headache_history":     ("medium",   "Is this similar to past headaches, or is this a new pattern?"),
    "allergies":                  ("medium",   "Any allergy to aspirin, NSAIDs, or other relevant medications?"),
    "assessment_plan":            ("low",      "Summarise the likely diagnosis and immediate plan for the chart."),
    "air_conditioning":           ("low",      "Does lack of cooling or heat exposure seem to be contributing?"),
}

def make_followup(fields, key):
    f = fields[key]
    severity, prompt = PROMPTS[key]
    if f["status"] == "review":
        prompt  = f"Please confirm: {f['label']} — current value: \"{f['value']}\""
        reason  = "Extracted with low confidence; needs confirmation."
        severity = "high"
    elif f["asked"] and not f["answered"]:
        reason = "Already asked; awaiting patient response."
    elif not f["unlocked"]:
        reason = "Unlocked by conversation context."
    else:
        reason = "Not yet covered in the conversation."
    return {"field_key": key, "label": fields[key]["label"], "severity": severity, "prompt": prompt, "reason": reason}

def top_followups(fields):
    scored = sorted(
        [key for key in fields if score(fields, key) > 0],
        key=lambda k: -score(fields, k)
    )
    return [make_followup(fields, k) for k in scored[:5]]

# ---------------------------------------------------------------------------
# Metrics and screen areas
# ---------------------------------------------------------------------------
def build_metrics(fields, followups):
    return {
        "nbFieldsFilled":   sum(1 for f in fields.values() if f["status"] == "filled"),
        "nbNeedsReview":    sum(1 for f in fields.values() if f["status"] == "review"),
        "nbActivePrompts":  len(followups),
    }

def build_screen_areas(fields, followups):
    summary_keys = ["chief_complaint", "thunderclap_screen", "neurologic_red_flags",
                    "medication_use", "assessment_plan"]
    return {
        "medical_form": [
            {"label": fields[k]["label"], "value": fields[k]["value"] or "Pending",
             "status": fields[k]["status"], "confidence": fields[k]["confidence"]}
            for k in summary_keys
        ],
        "followup": followups,
    }

# ---------------------------------------------------------------------------
# State builder
# ---------------------------------------------------------------------------
def build_state(tick):
    visible_count = min(len(SEGMENTS), tick + 1)
    timeline      = deepcopy(SEGMENTS[:visible_count])
    fields        = build_fields(visible_count)
    unlock_optional(fields, timeline)
    followups     = top_followups(fields)
    return {
        "updated_at":   float(visible_count),
        "metrics":      build_metrics(fields, followups),
        "timeline":     timeline,
        "fields":       fields,
        "followups":    followups,
        "screen_areas": build_screen_areas(fields, followups),
    }

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route('/')
def index():
    return jsonify({"message": "Headache protocol mock server v2",
                    "endpoints": ["/health", "/api/session", "/api/reset", "/api/state"]})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/session')
def session():
    tick    = app_state["tick"]
    payload = build_state(tick)
    if app_state["tick"] < len(SEGMENTS) - 1:
        app_state["tick"] += 1
    return jsonify(payload)

@app.route('/api/reset', methods=['GET', 'POST'])
def reset():
    app_state["tick"] = 0
    return jsonify({"ok": True, "tick": 0})

@app.route('/api/state')
def state():
    return jsonify({"tick": app_state["tick"],
                    "remaining": max(0, len(SEGMENTS) - 1 - app_state["tick"]),
                    "total_segments": len(SEGMENTS)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12345, debug=True)
