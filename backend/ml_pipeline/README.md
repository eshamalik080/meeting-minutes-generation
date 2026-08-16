# ml_pipeline/

Placeholder — real content lands in Phase 1. This package will hold clearly
separated, individually swappable functions for each ML stage
(`preprocess_audio`, `transcribe`, `diarize`, `extract_minutes`), each with a
mock implementation and a `USE_MOCK` flag so the rest of the app works
end-to-end before the real models are plugged in.
