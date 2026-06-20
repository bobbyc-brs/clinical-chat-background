# Mock Visit API

This folder contains:

- `headache-weather-scenario.txt`: a scripted doctor-patient scenario for UI testing.
- `mock_visit_api.py`: a Flask server that serves evolving state for `visit-001` on port `12345`.

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

The API will be available at:

```text
http://localhost:12345/api/sessions/visit-001
```

## Behavior

- Each GET to `/api/sessions/visit-001` reveals one more 3-second interval of the scripted conversation.
- The payload always includes `metrics`, `timeline`, `fields`, and `followups` in one response.
- Reset with:

```text
GET or POST /api/reset
```

## Front-end polling example

```javascript
setInterval(async () => {
  const resp = await fetch('http://localhost:12345/api/sessions/visit-001');
  const state = await resp.json();
  renderUI(state);
}, 3000);
```
