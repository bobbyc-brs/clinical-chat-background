# Clinical Conversation Prototype Repository

This repository bundle contains the browser-based clinical server dashboard prototype created in this session.

## Included today

| Folder | Contents |
|---|---|
| `clinical-web-app/` | Responsive browser prototype for the clinical server UI |

## Browser app

The browser app demonstrates:

- A merged doctor/patient conversation timeline.
- A configurable medical form area.
- Confidence-aware field states.
- Follow-up prompts when information is missing or uncertain.
- A layout that works on desktop screens and phones.

Main file:

- `clinical-web-app/clinical-server-dashboard.html`

Supporting file:

- `clinical-web-app/README.md`

## Recommended repo structure

Once your Git repository is initialized, a cleaner structure would be:

- `edge/` — patient and doctor device transcription clients
- `server/` — clinical processing backend and RPC ingest
- `web/` — responsive browser UI
- `docs/` — architecture notes, diagrams, prompt strategy, and deployment notes

## Suggested next commit plan

1. Add the browser dashboard first.
2. Add the backend clinical server next.
3. Add the edge transcription clients after that.
4. Add diagrams, architecture docs, and setup instructions.

## README purpose

This README is intentionally short so it can serve as the initial landing page for the repo. After the repo is created, it would make sense to expand it with:

- setup instructions,
- screenshots,
- architecture diagrams,
- environment variables,
- model/provider options,
- deployment notes.
