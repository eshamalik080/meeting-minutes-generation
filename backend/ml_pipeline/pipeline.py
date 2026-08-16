"""
Orchestrates the full pipeline: preprocess -> transcribe -> diarize ->
merge -> extract -> assemble the final MeetingMinutes object. This is
step 8 in the project plan ("Assemble structured Meeting Minutes object"),
and the function Phase 2's background job runner calls.
"""

from datetime import datetime
from pathlib import Path

from app.schemas import ActionItem, MeetingMinutes, TranscriptSegment

from .diarize import diarize
from .extract import extract_minutes
from .merge import format_transcript_for_llm, merge_transcript_with_speakers
from .preprocess import preprocess_audio
from .transcribe import transcribe


def run_pipeline(file_path: str, job_id: str) -> MeetingMinutes:
    """
    Input:
        file_path: path to the raw uploaded meeting audio/video file.
        job_id: id of the job this run belongs to (see app/jobs.py, Phase 2).
    Output:
        A fully populated, validated MeetingMinutes object.
    """
    cleaned_audio_path = preprocess_audio(file_path)

    transcript_segments = transcribe(cleaned_audio_path)
    speaker_segments = diarize(cleaned_audio_path)

    labeled_segments = merge_transcript_with_speakers(transcript_segments, speaker_segments)
    transcript_text = format_transcript_for_llm(labeled_segments)

    minutes = extract_minutes(transcript_text)

    duration_seconds = max((seg["end"] for seg in transcript_segments), default=None)
    participants = list(dict.fromkeys(seg["speaker"] for seg in labeled_segments))

    return MeetingMinutes(
        job_id=job_id,
        source_filename=Path(file_path).name,
        generated_at=datetime.now(),
        duration_seconds=duration_seconds,
        summary=minutes.get("summary", ""),
        key_topics=minutes.get("key_topics", []),
        decisions=minutes.get("decisions", []),
        action_items=[ActionItem(**item) for item in minutes.get("action_items", [])],
        transcript=[TranscriptSegment(**seg) for seg in labeled_segments],
        participants=participants,
    )
