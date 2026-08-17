"""
Stage 3: Speaker diarization.

Real counterpart: src/diarize.py -> diarize_audio() (pyannote.audio).
Owned by the teammate. Requires an HF_TOKEN env var and GPU for real use.
"""

from .config import USE_MOCK
from .mock_data import MOCK_SPEAKER_SEGMENTS


def diarize(audio_path: str) -> list[dict]:
    """
    Input:
        audio_path: path to a preprocessed audio file (output of preprocess_audio()).
    Output:
        List of speaker segment dicts, each shaped like:
            {"start": float, "end": float, "speaker": str}
        (start/end in seconds, speaker e.g. "SPEAKER_00"). This is a
        JSON-friendly reshape of src/diarize.py's
        `[(start, end, speaker), ...]` tuple list.

    Swap point: flip USE_MOCK in ml_pipeline/config.py once
    _real_diarize below calls diarize_audio(audio_path) from src/diarize.py
    and reshapes its tuples into this dict format.
    """
    if USE_MOCK:
        return _mock_diarize(audio_path)
    return _real_diarize(audio_path)


def _mock_diarize(audio_path: str) -> list[dict]:
    return [
        {"start": start, "end": end, "speaker": speaker}
        for start, end, speaker in MOCK_SPEAKER_SEGMENTS
    ]


def _real_diarize(audio_path: str) -> list[dict]:
    from src.diarize import diarize_audio
    segments = diarize_audio(audio_path)
    return [
        {"start": start, "end": end, "speaker": speaker}
        for start, end, speaker in segments
    ]
