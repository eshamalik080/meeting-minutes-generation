# ml_pipeline/

Four swappable stages, each wired to a single flag:

| Function | File | Real counterpart in `src/` |
|---|---|---|
| `preprocess_audio(file_path)` | `preprocess.py` | `preprocess.py::extract_and_normalize_audio` + `apply_vad` |
| `transcribe(audio_path)` | `transcribe.py` | `transcribe.py` (Whisper) |
| `diarize(audio_path)` | `diarize.py` | `diarize.py::diarize_audio` |
| `extract_minutes(transcript_text)` | `extract.py` | `extract_minutes.py::extract_minutes` |

`merge.py` is glue logic (timestamp-based speaker attribution), not an ML
stage — it's not gated by `USE_MOCK` and works unchanged with mock or real
data. `pipeline.py::run_pipeline()` chains all four stages and assembles
the final `MeetingMinutes` object (see `app/schemas.py`).

## Switching from mock to real

One flag, in `ml_pipeline/config.py`:

```python
USE_MOCK = os.getenv("USE_MOCK_ML", "true").strip().lower() != "false"
```

Set `USE_MOCK_ML=false` in `backend/.env` once the `_real_*` function in
each stage file is implemented. Until then, every stage returns data from
`mock_data.py` — a single fabricated 3-speaker meeting reused everywhere so
the transcript, diarization, and extracted minutes are always internally
consistent, regardless of what audio file is actually uploaded.

Each stage's docstring documents the exact input/output shape the rest of
the app expects — match that shape in `_real_*` and nothing else needs to
change. See [`ML_INTEGRATION.md`](../../ML_INTEGRATION.md) at the repo
root for the full walkthrough, including one small required refactor in
`src/transcribe.py` and exact code for each `_real_*` function.

## Try it

```bash
cd backend
source venv/bin/activate
python test_pipeline.py
```

Runs the whole mocked pipeline end-to-end and prints the resulting
`MeetingMinutes` JSON. No real audio file is required.
