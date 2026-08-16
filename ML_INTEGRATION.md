# Plugging the real ML pipeline into the backend

This is for the ML teammate: everything you need to swap your real
Whisper/pyannote/spaCy/Ollama code (`src/`) in for the mock pipeline the
web app currently runs on. Nothing here requires you to touch anything
outside `src/` and the four files listed below — the web app, API, job
orchestration, and exports were all built and tested against the *shape*
of your code, not a stand-in for it.

## How the boundary works

`backend/ml_pipeline/` has four stage files, each with a mock
implementation and a `_real_*` stub:

| File | Function | Your file |
|---|---|---|
| `preprocess.py` | `preprocess_audio(file_path) -> str` | `src/preprocess.py` |
| `transcribe.py` | `transcribe(audio_path) -> list[dict]` | `src/transcribe.py` |
| `diarize.py` | `diarize(audio_path) -> list[dict]` | `src/diarize.py` |
| `extract.py` | `extract_minutes(transcript_text) -> dict` | `src/extract_minutes.py` |

One flag controls all four: `ml_pipeline/config.py`'s `USE_MOCK`, driven
by `USE_MOCK_ML` in `backend/.env`. Flip it to `false` once you've filled
in the `_real_*` functions below — you don't need to touch `config.py`
itself, and it already does one thing for you: it puts the repo root on
`sys.path`, so `from src.diarize import diarize_audio` works from inside
`backend/` even though `src/` is a sibling directory, not a subpackage of
`backend/`. (`src/` has no `__init__.py`, but that's fine — Python treats
it as a namespace package as long as the repo root is importable.)

## Before you start: one thing in `src/transcribe.py` needs a small refactor

Every other file in `src/` guards its script-only code behind
`if __name__ == "__main__":`, so importing the module just defines
functions — safe. **`transcribe.py` doesn't.** Right now the whole file is
top-level script code:

```python
import torch
import whisper
import time

print("CUDA available:", torch.cuda.is_available())
model = whisper.load_model("base", device="cuda")
...
result = model.transcribe("data/processed_audio.wav")
```

Importing this as-is would load a Whisper model and transcribe a
hardcoded file path the moment Python sees the `import` statement —
including every time the backend process starts. You'll want to wrap it
in a function, and ideally cache the loaded model so it's not reloaded on
every request:

```python
import torch
import whisper

_model = None

def transcribe_audio(audio_path: str, model_name: str = "base") -> dict:
    global _model
    if _model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _model = whisper.load_model(model_name, device=device)
    return _model.transcribe(audio_path, word_timestamps=True)
```

(`device="cuda" if torch.cuda.is_available() else "cpu"` instead of your
current hardcoded `"cuda"` — worth doing so this doesn't hard-crash on a
machine without a GPU. Your call whether to do the same in `diarize.py`,
which has the same hardcode.)

This is the only change needed in `src/` itself. Everything else below
lives in `backend/ml_pipeline/`.

## Filling in the four `_real_*` functions

Each one already has a docstring in the repo describing the exact
input/output shape expected — the snippets below are the actual
integration code, not just a sketch.

### `preprocess.py`

```python
def _real_preprocess_audio(file_path: str) -> str:
    from src.preprocess import extract_and_normalize_audio
    return extract_and_normalize_audio(file_path)
```

Note: your `apply_vad()` currently only *detects* speech segments — it
doesn't trim silence out of the audio file itself, so there's nothing for
`preprocess_audio()` to do with its return value yet. If you want VAD to
actually shorten the audio before transcription, that's an enhancement to
`apply_vad` itself (have it write a trimmed WAV), not something this
integration layer needs to change.

### `transcribe.py`

```python
def _real_transcribe(audio_path: str) -> list[dict]:
    from src.transcribe import transcribe_audio
    result = transcribe_audio(audio_path)
    return [
        {"start": seg["start"], "end": seg["end"], "text": seg["text"]}
        for seg in result["segments"]
    ]
```

(Uses the refactored `transcribe_audio` from the section above.)

### `diarize.py`

```python
def _real_diarize(audio_path: str) -> list[dict]:
    from src.diarize import diarize_audio
    segments = diarize_audio(audio_path)
    return [
        {"start": start, "end": end, "speaker": speaker}
        for start, end, speaker in segments
    ]
```

Needs `HF_TOKEN` set in `backend/.env` (a HuggingFace access token with
the `pyannote/speaker-diarization-3.1` gated model's terms accepted on
huggingface.co) and a CUDA GPU, since `diarize_audio` hardcodes
`.to(torch.device("cuda"))`.

### `extract.py`

```python
def _real_extract_minutes(transcript_with_speakers: str) -> dict:
    from src.extract_minutes import extract_minutes as real_extract_minutes
    return real_extract_minutes(transcript_with_speakers, model_name="qwen2.5")
```

Needs a local Ollama server running (`ollama serve`) with the model
pulled (`ollama pull qwen2.5`), and the `ollama` Python package installed
— it's imported in `src/extract_minutes.py` but isn't currently listed in
the root `requirements.txt`, so `pip install ollama` separately or add it
there yourself.

One thing already handled on the web app's side: if the LLM doesn't
return valid JSON, `extract_minutes()` returns
`{"error": "invalid_json", "raw_output": ...}` instead of raising.
`ml_pipeline/pipeline.py` checks for that `error` key and raises, which
the job runner catches and marks the job `failed` with your raw LLM
output as the error message — so a bad LLM response shows up as a clear
failure in the UI instead of a silently empty summary.

## Environment setup checklist

1. Install the heavy ML deps into the **same** venv the backend runs in
   (either `pip install -r requirements.txt` from the repo root into
   `backend/venv`, or point the backend at your existing ML venv) —
   `backend/requirements.txt` alone only has FastAPI-level dependencies.
2. `pip install ollama` (see above — missing from `requirements.txt`).
3. Set in `backend/.env`:
   ```
   USE_MOCK_ML=false
   HF_TOKEN=<your huggingface token>
   ```
4. `ollama serve` running, with `ollama pull qwen2.5` done at least once.
5. A CUDA-capable GPU available on whatever machine runs the backend.

## Testing strategy — smallest surface area first

Don't flip `USE_MOCK_ML=false` and go straight to the full app. Test each
stage standalone first, from `backend/` with the venv active:

```python
python -c "
from ml_pipeline.preprocess import _real_preprocess_audio
print(_real_preprocess_audio('/path/to/a/real/meeting.mp3'))
"
```

Repeat for `_real_transcribe`, `_real_diarize`, `_real_extract_minutes`
individually — each takes the previous stage's output. Once all four work
in isolation, flip `USE_MOCK_ML=false` and run:

```bash
python test_pipeline.py
```

(Same script used to verify the mock pipeline in Phase 1 — now exercises
your real code end-to-end and prints the resulting `MeetingMinutes` JSON.)
Only after that passes, start the full app (`uvicorn` + `npm run dev`) and
test through the UI.

## Known limitations to expect

- **Won't run on the Phase 7 Render deployment.** Render's free tier has
  no GPU and no way to run a local Ollama server — real mode is for local
  (or your own GPU-backed) environments only. The deployed demo will stay
  on mock mode; that's expected, not a bug to chase.
- **First request after startup will be slow** — model loading (Whisper,
  pyannote) happens on first real call, not at server startup, so the
  first upload after `USE_MOCK_ML=false` takes noticeably longer than
  subsequent ones.
- **Rollback is one line.** If real mode misbehaves mid-demo, set
  `USE_MOCK_ML=true` and restart — nothing else needs to change.
