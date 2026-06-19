# Clinical Conversation Capture and Form Population Repo

This repository bundles the key prototype pieces discussed so far:

- edge transcription clients,
- PyRPC-based transcript forwarding,
- a clinical server that receives and processes those RPC messages,
- a configurable form template,
- and a browser-based dashboard for review.

## Repository structure

| Path | Purpose |
|---|---|
| `edge-clients/` | Local microphone capture, speech-to-text, confidence tracking, and RPC forwarding |
| `clinical-server/` | Server that receives transcript RPC messages, applies extraction, and serves API/UI |
| `web-ui/` | Browser-based dashboard |
| `docs/` | Architecture notes |

## Main files

### Edge clients
- `edge-clients/app.py`
- `edge-clients/rpc_server_example.py`
- `edge-clients/requirements.txt`

### Clinical server
- `clinical-server/clinical_server.py`
- `clinical-server/form_template.yaml`
- `clinical-server/requirements.txt`

### Browser UI
- `web-ui/clinical-server-dashboard.html`

## Run order

### 1. Start the clinical server

```bash
cd clinical-server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python clinical_server.py
```

This starts:
- a PyRPC listener on port `9090`,
- a browser UI/API server on port `8080`.

### 2. Open the browser dashboard

Open:

```text
http://localhost:8080
```

### 3. Start edge clients

Example patient device:

```bash
cd edge-clients
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py --speaker-role patient --device-id patient-device --session-id visit-001 --rpc-host 127.0.0.1 --rpc-port 9090
```

Example doctor device:

```bash
python app.py --speaker-role doctor --device-id doctor-device --session-id visit-001 --rpc-host 127.0.0.1 --rpc-port 9090
```

## OpenRouter configuration

To enable model-backed extraction, set:

```bash
export OPENROUTER_API_KEY=your_key_here
export OPENROUTER_MODEL=cohere/north-mini-code:free
```

If no API key is set, the clinical server falls back to heuristic extraction.

## Notes

- `whisper-timestamped` is used for timestamps and confidence-aware transcription.
- The server is the component that receives transcript RPC messages and processes them.
- The browser app is a front-end for that server, not the inference engine itself.
