// Mock server mirroring the real clinical-server response shape
// Run with: npm run mock  (port 2222)
// POST /api/demo/load resets the conversation to t=0

import http from "http"

const PORT = 2222

// Matches Bobby's actual field set from /api/session
const FIELD_DEFS = [
  { key: "chief_complaint",   label: "Chief Complaint" },
  { key: "onset",             label: "Onset" },
  { key: "frequency",         label: "Frequency" },
  { key: "location",          label: "Location" },
  { key: "severity",          label: "Severity" },
  { key: "associated_symptoms", label: "Associated Symptoms" },
  { key: "relieving_factors", label: "Relieving Factors" },
  { key: "hydration_context", label: "Hydration / Heat Context" },
  { key: "red_flags",         label: "Red Flags" },
  { key: "blood_pressure",    label: "Blood Pressure" },
  { key: "sleep_disruption",  label: "Sleep Disruption" },
  { key: "asa_allergy",       label: "ASA Allergy" },
  { key: "treatment_plan",    label: "Treatment Plan" },
  { key: "followup_interval", label: "Follow-up Interval" },
  { key: "air_conditioning",  label: "Air Conditioning" },
]

const CONVERSATION_SCRIPT = [
  { t:  1500, segment_id: 1,  start:  0, end:  3, speaker_role: "doctor",  device_id: "doctor-device",  confidence: 0.97, text: "Hi, what brings you in today?" },
  { t:  3500, segment_id: 2,  start:  3, end:  6, speaker_role: "patient", device_id: "patient-device", confidence: 0.94, text: "I've been getting headaches since the weather started getting warmer." },
  { t:  6000, segment_id: 3,  start:  6, end:  9, speaker_role: "doctor",  device_id: "doctor-device",  confidence: 0.96, text: "When did you first notice them?" },
  { t:  8000, segment_id: 4,  start:  9, end: 12, speaker_role: "patient", device_id: "patient-device", confidence: 0.90, text: "About two weeks ago, when the hot days started." },
  { t: 10000, segment_id: 5,  start: 12, end: 15, speaker_role: "doctor",  device_id: "doctor-device",  confidence: 0.96, text: "How often are you getting the headaches?" },
  { t: 12000, segment_id: 6,  start: 15, end: 18, speaker_role: "patient", device_id: "patient-device", confidence: 0.89, text: "Almost every afternoon." },
  { t: 14000, segment_id: 7,  start: 18, end: 21, speaker_role: "doctor",  device_id: "doctor-device",  confidence: 0.97, text: "Where do you feel the pain?" },
  { t: 16000, segment_id: 8,  start: 21, end: 24, speaker_role: "patient", device_id: "patient-device", confidence: 0.88, text: "Mostly across my forehead and sometimes behind my eyes." },
  { t: 18000, segment_id: 9,  start: 24, end: 27, speaker_role: "doctor",  device_id: "doctor-device",  confidence: 0.97, text: "How severe are they, from zero to ten?" },
  { t: 20000, segment_id: 10, start: 27, end: 30, speaker_role: "patient", device_id: "patient-device", confidence: 0.86, text: "Usually around a six." },
  { t: 22000, segment_id: 11, start: 30, end: 33, speaker_role: "doctor",  device_id: "doctor-device",  confidence: 0.96, text: "Any nausea, vision changes, or dizziness?" },
  { t: 24000, segment_id: 12, start: 33, end: 36, speaker_role: "patient", device_id: "patient-device", confidence: 0.84, text: "No nausea, but I do feel a little light-sensitive." },
  { t: 26000, segment_id: 13, start: 36, end: 39, speaker_role: "doctor",  device_id: "doctor-device",  confidence: 0.95, text: "Does anything make the headaches better or worse?" },
  { t: 28000, segment_id: 14, start: 39, end: 43, speaker_role: "patient", device_id: "patient-device", confidence: 0.81, text: "Lying down in a dark room helps. They get worse in the sun." },
]

const FIELD_TIMELINE = [
  { t:  3500, key: "chief_complaint",    label: "Chief Complaint",        value: "Headaches starting with warmer weather",           confidence: 0.94, status: "filled",  evidence: ["I've been getting headaches since the weather started getting warmer."] },
  { t:  8000, key: "onset",             label: "Onset",                  value: "About two weeks ago when hot weather started",     confidence: 0.90, status: "filled",  evidence: ["About two weeks ago, when the hot days started."] },
  { t: 12000, key: "frequency",         label: "Frequency",              value: "Almost every afternoon",                           confidence: 0.89, status: "filled",  evidence: ["Almost every afternoon."] },
  { t: 16000, key: "location",          label: "Location",               value: "Forehead and sometimes behind the eyes",           confidence: 0.88, status: "filled",  evidence: ["Mostly across my forehead and sometimes behind my eyes."] },
  { t: 20000, key: "severity",          label: "Severity",               value: "6 / 10",                                           confidence: 0.86, status: "filled",  evidence: ["Usually around a six."] },
  { t: 24000, key: "associated_symptoms", label: "Associated Symptoms",  value: "Light sensitivity; denies nausea",                 confidence: 0.84, status: "review",  evidence: ["No nausea, but I do feel a little light-sensitive."] },
  { t: 28000, key: "relieving_factors", label: "Relieving Factors",      value: "Dark room, lying down; worsens in sunlight",       confidence: 0.81, status: "filled",  evidence: ["Lying down in a dark room helps. They get worse in the sun."] },
]

const FOLLOWUPS_TIMELINE = [
  { from:     0, until: 28000,    followup: { field_key: "relieving_factors",  severity: "medium", prompt: "Ask about relieving factors.",           reason: "missing" } },
  { from:     0, until: Infinity, followup: { field_key: "hydration_context",  severity: "medium", prompt: "Ask about hydration / heat context.",    reason: "missing" } },
  { from:     0, until: Infinity, followup: { field_key: "red_flags",          severity: "medium", prompt: "Ask about red flags.",                   reason: "missing" } },
  { from:     0, until: Infinity, followup: { field_key: "blood_pressure",     severity: "medium", prompt: "Ask about blood pressure.",              reason: "missing" } },
  { from:     0, until: Infinity, followup: { field_key: "sleep_disruption",   severity: "medium", prompt: "Ask about sleep disruption.",            reason: "missing" } },
  { from:     0, until: Infinity, followup: { field_key: "asa_allergy",        severity: "medium", prompt: "Ask about ASA allergy.",                 reason: "missing" } },
  { from:     0, until: Infinity, followup: { field_key: "treatment_plan",     severity: "medium", prompt: "Ask about treatment plan.",              reason: "missing" } },
  { from:     0, until: Infinity, followup: { field_key: "followup_interval",  severity: "medium", prompt: "Ask about follow-up interval.",          reason: "missing" } },
  { from:     0, until: Infinity, followup: { field_key: "air_conditioning",   severity: "medium", prompt: "Ask about air conditioning.",            reason: "missing" } },
  { from: 24000, until: Infinity, followup: { field_key: "associated_symptoms", severity: "high", prompt: "Confirm associated symptoms.",           reason: "low_confidence" } },
]

let startTime = Date.now()

function reset() { startTime = Date.now() }

function getSession() {
  const elapsed = Date.now() - startTime

  const timeline = CONVERSATION_SCRIPT
    .filter(s => s.t <= elapsed)
    .map(({ t: _t, ...entry }) => entry)

  // Start all fields as missing (with label)
  const fields = {}
  for (const def of FIELD_DEFS) {
    fields[def.key] = { key: def.key, label: def.label, value: null, confidence: 0, evidence: [], status: "missing" }
  }
  // Apply updates in order
  for (const update of FIELD_TIMELINE) {
    if (update.t <= elapsed) {
      const { t: _t, ...rest } = update
      fields[update.key] = rest
    }
  }

  const followups = FOLLOWUPS_TIMELINE
    .filter(f => f.from <= elapsed && elapsed < f.until)
    .map(f => f.followup)

  const fieldValues = Object.values(fields)
  const metrics = {
    nbFieldsFilled:  fieldValues.filter(f => f.status === "filled").length,
    nbNeedsReview:   fieldValues.filter(f => f.status === "review").length,
    nbActivePrompts: followups.length,
  }

  // updated_at is relative seconds (matching real server)
  return { updated_at: elapsed / 1000, metrics, timeline, fields, followups }
}

function cors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*")
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, ngrok-skip-browser-warning")
}

function json(res, data, status = 200) {
  cors(res)
  res.writeHead(status, { "Content-Type": "application/json" })
  res.end(JSON.stringify(data))
}

const server = http.createServer((req, res) => {
  if (req.method === "OPTIONS") { cors(res); res.writeHead(204); res.end(); return }

  if (req.method === "GET"  && req.url === "/api/session")    return json(res, getSession())
  if (req.method === "POST" && req.url === "/api/demo/load")  { reset(); return json(res, getSession()) }
  if (req.method === "GET"  && req.url === "/health")         return json(res, { status: "ok" })

  cors(res); res.writeHead(404); res.end()
})

server.listen(PORT, () => {
  console.log(`Mock server on http://localhost:${PORT}`)
  console.log(`  GET  /api/session   — live session (advances over ~30s)`)
  console.log(`  POST /api/demo/load — reset to t=0`)
  console.log(`  GET  /health        — health check`)
})
