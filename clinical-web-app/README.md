# Browser-based Clinical Server UI

This is a responsive browser-based prototype for the clinical server application.

## What it demonstrates

- A screen-friendly and phone-friendly dashboard layout.
- Multiple encounter sessions.
- A merged doctor/patient conversation timeline.
- A configurable medical form whose fields and relative layout come from template metadata.
- Confidence-aware field states: filled, review, and missing.
- On-screen follow-up prompts when information is missing or uncertain.

## Important scope note

This HTML app is a front-end prototype. In production, the browser UI would connect to a backend clinical server that:
- receives RPC transcript messages,
- merges encounter context,
- uses structured LLM extraction,
- optionally uses RAG for reusable form guidance,
- pushes updated field values and prompt queues to the browser.

## Suggested production stack

- Backend: Python FastAPI or Flask + RPC listener service.
- Browser UI: this responsive dashboard pattern.
- LLM extraction: schema-driven outputs per form template.
- Retrieval: form instructions, specialty guidance, synonym lists, previous template rules.
- Real-time UI updates: WebSocket or Server-Sent Events.
