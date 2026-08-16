"""
Stage 1: Audio extraction & preprocessing.

Real counterpart: src/preprocess.py -> extract_and_normalize_audio()
(pydub + ffmpeg, converts to 16kHz mono WAV) and apply_vad() (webrtcvad,
trims silence). Both are the teammate's responsibility; this module owns
the plug point that the rest of the backend calls.
"""

import shutil
from pathlib import Path

from .config import USE_MOCK


def preprocess_audio(file_path: str) -> str:
    """
    Input:
        file_path: path to the raw uploaded meeting file (mp3/mp4/wav/etc).
    Output:
        Path (str) to a cleaned, normalized audio file ready for transcription
        (in the real pipeline: 16kHz mono WAV with silence trimmed).

    Swap point: flip USE_MOCK to False in ml_pipeline/config.py (or set
    USE_MOCK_ML=false in .env) once _real_preprocess_audio below calls into
    src/preprocess.py's extract_and_normalize_audio() + apply_vad().
    """
    if USE_MOCK:
        return _mock_preprocess_audio(file_path)
    return _real_preprocess_audio(file_path)


def _mock_preprocess_audio(file_path: str) -> str:
    """Copies the input file to a '_normalized.wav' sibling path, unchanged.
    Does not actually resample/trim silence — just proves the plumbing works."""
    src = Path(file_path)
    output_path = src.with_name(f"{src.stem}_normalized.wav")
    if src.exists():
        shutil.copyfile(src, output_path)
    else:
        # Lets the test script / pipeline run without a real audio asset on disk.
        output_path.touch()
    return str(output_path)


def _real_preprocess_audio(file_path: str) -> str:
    raise NotImplementedError(
        "Wire this up to src/preprocess.py: "
        "extract_and_normalize_audio(file_path) then apply_vad() on the result."
    )
