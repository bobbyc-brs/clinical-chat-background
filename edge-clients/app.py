import argparse
import json
import queue
import signal
import sys
import threading
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

import numpy as np
import sounddevice as sd

try:
    import whisper_timestamped as whisper
except ImportError as exc:
    raise SystemExit("Missing dependency 'whisper-timestamped'. Install requirements first.") from exc

try:
    from pyrpc.RPCClient import RPCClient
except Exception:
    RPCClient = None

SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_SECONDS = 0.5
DEFAULT_SEGMENT_SECONDS = 5.0

@dataclass
class TranscriptAlternative:
    text: str
    score: Optional[float] = None

@dataclass
class WordResult:
    text: str
    start: float
    end: float
    confidence: Optional[float]
    alternatives: List[TranscriptAlternative]

@dataclass
class SegmentResult:
    segment_id: int
    start: float
    end: float
    text: str
    confidence: Optional[float]
    avg_logprob: Optional[float]
    no_speech_prob: Optional[float]
    alternatives: List[TranscriptAlternative]
    words: List[WordResult]

class AudioBuffer:
    def __init__(self, sample_rate: int, channels: int):
        self.sample_rate = sample_rate
        self.channels = channels
        self.q: "queue.Queue[np.ndarray]" = queue.Queue()
        self.closed = False

    def callback(self, indata, frames, time_info, status):
        if status:
            print(f"[audio] {status}", file=sys.stderr)
        self.q.put(indata.copy())

    def read_chunk(self, seconds: float) -> np.ndarray:
        target_samples = int(seconds * self.sample_rate)
        chunks = []
        collected = 0
        while collected < target_samples and not self.closed:
            try:
                block = self.q.get(timeout=1.0)
            except queue.Empty:
                continue
            mono = block.reshape(-1, self.channels).mean(axis=1)
            chunks.append(mono)
            collected += len(mono)
        if not chunks:
            return np.zeros(0, dtype=np.float32)
        audio = np.concatenate(chunks).astype(np.float32)
        if len(audio) > target_samples:
            audio = audio[:target_samples]
        return audio

    def close(self):
        self.closed = True

class Forwarder:
    def __init__(self, host: Optional[str], port: Optional[int], method: str):
        self.client = None
        self.method = method
        if host and port:
            if RPCClient is None:
                raise RuntimeError("PyRPC client import failed. Install 'fspyrpc' to enable forwarding.")
            self.client = RPCClient(host, port)

    def send(self, payload: Dict[str, Any]):
        if not self.client:
            return
        getattr(self.client, self.method)(payload)

class Transcriber:
    def __init__(self, model_name: str, device: Optional[str], language: Optional[str], accurate: bool):
        self.model = whisper.load_model(model_name, device=device)
        self.language = language
        self.accurate = accurate

    def transcribe_window(self, audio: np.ndarray, offset_seconds: float) -> Dict[str, Any]:
        kwargs = {
            "language": self.language,
            "vad": True,
            "compute_word_confidence": True,
            "remove_punctuation_from_words": False,
            "condition_on_previous_text": False,
        }
        if self.accurate:
            kwargs.update({"beam_size": 5, "best_of": 5, "temperature": (0.0, 0.2, 0.4, 0.6)})
        else:
            kwargs.update({"temperature": 0.0})
        result = whisper.transcribe(self.model, audio, **kwargs)
        result["_offset_seconds"] = offset_seconds
        return result

def build_segment_alternatives(segment: Dict[str, Any]) -> List[TranscriptAlternative]:
    alts = []
    primary = segment.get("text", "").strip()
    if primary:
        alts.append(TranscriptAlternative(text=primary, score=segment.get("confidence")))
    uncertain = [w.get("text", "").strip() for w in (segment.get("words", []) or []) if (w.get("confidence") or 1.0) < 0.6 and w.get("text")]
    if uncertain:
        alts.append(TranscriptAlternative(text=f"Possible uncertainty around: {' '.join(uncertain)}"))
    if segment.get("no_speech_prob", 0) > 0.5:
        alts.append(TranscriptAlternative(text="Possible silence or non-speech segment", score=segment.get("no_speech_prob")))
    return alts[:3]

def build_word_alternatives(word: Dict[str, Any]) -> List[TranscriptAlternative]:
    conf = word.get("confidence")
    text = word.get("text", "").strip()
    alts = [TranscriptAlternative(text=text, score=conf)] if text else []
    if conf is not None and conf < 0.5 and text:
        alts.append(TranscriptAlternative(text=f"{text} (?)", score=conf))
    return alts[:2]

def normalize_result(raw: Dict[str, Any], next_segment_id: int) -> List[SegmentResult]:
    offset = raw.get("_offset_seconds", 0.0)
    out: List[SegmentResult] = []
    for idx, seg in enumerate(raw.get("segments", []) or []):
        words = []
        for w in seg.get("words", []) or []:
            words.append(WordResult(text=w.get("text", "").strip(), start=offset + float(w.get("start", 0.0)), end=offset + float(w.get("end", 0.0)), confidence=w.get("confidence"), alternatives=build_word_alternatives(w)))
        out.append(SegmentResult(segment_id=next_segment_id + idx, start=offset + float(seg.get("start", 0.0)), end=offset + float(seg.get("end", 0.0)), text=seg.get("text", "").strip(), confidence=seg.get("confidence"), avg_logprob=seg.get("avg_logprob"), no_speech_prob=seg.get("no_speech_prob"), alternatives=build_segment_alternatives(seg), words=words))
    return out

def run(args):
    stop_event = threading.Event()
    def handle_signal(signum, frame):
        stop_event.set()
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    audio_buffer = AudioBuffer(SAMPLE_RATE, CHANNELS)
    transcriber = Transcriber(args.model, args.device, args.language, args.accurate)
    forwarder = Forwarder(args.rpc_host, args.rpc_port, args.rpc_method)
    global_offset = 0.0
    segment_counter = 0

    print("Listening... Press Ctrl+C to stop.")
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="float32", blocksize=int(SAMPLE_RATE * BLOCK_SECONDS), callback=audio_buffer.callback):
        while not stop_event.is_set():
            window = audio_buffer.read_chunk(args.segment_seconds)
            if window.size == 0:
                continue
            raw = transcriber.transcribe_window(window, global_offset)
            segments = normalize_result(raw, segment_counter)
            if not segments:
                global_offset += len(window) / SAMPLE_RATE
                continue
            payload = {
                "event": "transcript_batch",
                "session_id": args.session_id,
                "device_id": args.device_id,
                "speaker_role": args.speaker_role,
                "captured_at": time.time(),
                "language": raw.get("language"),
                "language_probs": raw.get("language_probs", {}),
                "segments": [asdict(s) for s in segments],
            }
            for seg in segments:
                print(f"[{seg.start:8.2f}-{seg.end:8.2f}] {args.speaker_role} conf={seg.confidence!s:>5} text={seg.text}")
            if args.jsonl:
                with open(args.jsonl, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
            try:
                forwarder.send(payload)
            except Exception as exc:
                print(f"[rpc] forward failed: {exc}", file=sys.stderr)
            segment_counter += len(segments)
            global_offset += len(window) / SAMPLE_RATE
    audio_buffer.close()

def parse_args():
    p = argparse.ArgumentParser(description="Real-time microphone transcription with confidence and PyRPC forwarding")
    p.add_argument("--session-id", default="visit-001")
    p.add_argument("--device-id", default="patient-device")
    p.add_argument("--speaker-role", choices=["patient", "doctor"], default="patient")
    p.add_argument("--model", default="base")
    p.add_argument("--device", default=None)
    p.add_argument("--language", default=None)
    p.add_argument("--segment-seconds", type=float, default=DEFAULT_SEGMENT_SECONDS)
    p.add_argument("--accurate", action="store_true")
    p.add_argument("--jsonl", default="transcripts.jsonl")
    p.add_argument("--rpc-host", default=None)
    p.add_argument("--rpc-port", type=int, default=None)
    p.add_argument("--rpc-method", default="push_transcript")
    return p.parse_args()

if __name__ == "__main__":
    run(parse_args())
