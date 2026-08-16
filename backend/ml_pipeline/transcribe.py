"""
Stage 2: Speech-to-text.

Real counterpart: src/transcribe.py (openai-whisper, model.transcribe()).
Owned by the teammate.
"""

from .config import USE_MOCK
from .mock_data import MOCK_TRANSCRIPT_SEGMENTS


def transcribe(audio_path: str) -> list[dict]:
    """
    Input:
        audio_path: path to a preprocessed audio file (output of preprocess_audio()).
    Output:
        List of segment dicts, each shaped like:
            {"start": float, "end": float, "text": str}
        (start/end in seconds). This mirrors Whisper's
        `model.transcribe(path, word_timestamps=True)["segments"]` shape,
        trimmed to the three fields the rest of the app actually uses.

    Swap point: flip USE_MOCK in ml_pipeline/config.py once
    _real_transcribe below calls whisper.load_model(...).transcribe(audio_path).
    """
    if USE_MOCK:
        return _mock_transcribe(audio_path)
    return _real_transcribe(audio_path)


def _mock_transcribe(audio_path: str) -> list[dict]:
    return [dict(seg) for seg in MOCK_TRANSCRIPT_SEGMENTS]


def _real_transcribe(audio_path: str) -> list[dict]:
    raise NotImplementedError(
        "Wire this up to src/transcribe.py: load the Whisper model once at "
        "module import (not per-call), then return "
        "whisper_result['segments'] reshaped to [{'start','end','text'}, ...]."
    )
