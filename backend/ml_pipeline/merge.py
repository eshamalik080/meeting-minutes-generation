"""
Glue step between the ML stages and the final Meeting Minutes object.

Not gated by USE_MOCK — this is plain deterministic logic (nearest-speaker
matching by timestamp midpoint), not a model, so it works unchanged whether
transcribe()/diarize() are mocked or real. Equivalent in spirit to
src/clean_ner.py's merge_transcript_with_speakers(), adapted to work off the
list[dict] shapes transcribe() and diarize() return here rather than a raw
Whisper result dict.
"""


def merge_transcript_with_speakers(
    transcript_segments: list[dict],
    speaker_segments: list[dict],
) -> list[dict]:
    """
    Input:
        transcript_segments: output of transcribe() -> [{"start","end","text"}, ...]
        speaker_segments: output of diarize() -> [{"start","end","speaker"}, ...]
    Output:
        List of speaker-labeled segment dicts:
            [{"start": float, "end": float, "speaker": str, "text": str}, ...]
        Speaker is resolved by finding which diarization segment contains
        each transcript segment's midpoint timestamp; falls back to
        "UNKNOWN" if no speaker segment covers that point.
    """
    labeled = []
    for seg in transcript_segments:
        mid = (seg["start"] + seg["end"]) / 2
        speaker = "UNKNOWN"
        for spk_seg in speaker_segments:
            if spk_seg["start"] <= mid <= spk_seg["end"]:
                speaker = spk_seg["speaker"]
                break
        labeled.append({
            "start": seg["start"],
            "end": seg["end"],
            "speaker": speaker,
            "text": seg["text"].strip(),
        })
    return labeled


def format_transcript_for_llm(labeled_segments: list[dict]) -> str:
    """
    Input: output of merge_transcript_with_speakers() above.
    Output: a single string like:
        "Speaker SPEAKER_00: text...\\nSpeaker SPEAKER_01: text..."
    This is the exact input shape src/extract_minutes.py's extract_minutes()
    expects as its `transcript` argument.
    """
    return "\n".join(
        f"Speaker {seg['speaker']}: {seg['text']}" for seg in labeled_segments
    )
