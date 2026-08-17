"""
Stage 4: LLM-based structured extraction.

Real counterpart: src/extract_minutes.py -> extract_minutes() (Ollama +
Qwen2.5, prompt engineering). Owned by the teammate. Requires a local
Ollama server running the model for real use.
"""

from .config import USE_MOCK
from .mock_data import MOCK_MINUTES


def extract_minutes(transcript_with_speakers: str) -> dict:
    """
    Input:
        transcript_with_speakers: speaker-labeled transcript text, e.g.
            "Speaker SPEAKER_00: ...\\nSpeaker SPEAKER_01: ..."
            (output of merge.format_transcript_for_llm()).
    Output:
        dict shaped exactly like src/extract_minutes.py's return value:
            {
              "summary": str,
              "key_topics": list[str],
              "decisions": list[str],
              "action_items": [{"task": str, "owner": str, "deadline": str}, ...]
            }

    Swap point: flip USE_MOCK in ml_pipeline/config.py once
    _real_extract_minutes below calls extract_minutes() from
    src/extract_minutes.py with the same transcript string.
    """
    if USE_MOCK:
        return _mock_extract_minutes(transcript_with_speakers)
    return _real_extract_minutes(transcript_with_speakers)


def _mock_extract_minutes(transcript_with_speakers: str) -> dict:
    return {
        "summary": MOCK_MINUTES["summary"],
        "key_topics": list(MOCK_MINUTES["key_topics"]),
        "decisions": list(MOCK_MINUTES["decisions"]),
        "action_items": [dict(item) for item in MOCK_MINUTES["action_items"]],
    }


def _real_extract_minutes(transcript_with_speakers: str) -> dict:
    from src.extract_minutes import extract_minutes as real_extract_minutes
    return real_extract_minutes(transcript_with_speakers, model_name="qwen2.5")
