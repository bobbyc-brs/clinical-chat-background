# Clinical Conversation System Architecture

## Components

1. **Patient edge client**
   - Captures microphone audio.
   - Converts speech to text locally.
   - Sends transcript batches with timestamps and confidence to the clinical server over RPC.

2. **Doctor edge client**
   - Captures microphone audio.
   - Converts speech to text locally.
   - Sends transcript batches with timestamps and confidence to the clinical server over RPC.

3. **Clinical server**
   - Receives transcript batches over PyRPC.
   - Merges both streams into one encounter timeline.
   - Uses configurable form templates.
   - Applies LLM-backed or heuristic extraction.
   - Produces follow-up questions when information is missing, inconsistent, or uncertain.

4. **Browser UI**
   - Displays the timeline, field values, confidence, and follow-up prompts.
   - Works on both desktop screens and phones.

## Inference path

- Primary path: OpenRouter structured output, configured through environment variables.
- Fallback path: heuristic extraction when no API key is present or the LLM call fails.

## Data flow

1. Patient / doctor microphone audio is transcribed locally.
2. Transcript batches are forwarded to `handle_push_transcript()` on the clinical server.
3. The clinical server updates encounter state.
4. The server extracts field values and prompt suggestions.
5. The browser app reads the latest session state via HTTP endpoints.
