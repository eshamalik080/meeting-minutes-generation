"""
Orchestrates the full pipeline: preprocess -> transcribe -> diarize ->
merge -> extract -> assemble the final MeetingMinutes object. This is
step 8 in the project plan ("Assemble structured Meeting Minutes object"),
and the function Phase 2's background job runner calls.
"""

from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from app.schemas import ActionItem, MeetingMinutes, TranscriptSegment

from .diarize import diarize
from .extract import extract_minutes
from .merge import format_transcript_for_llm, merge_transcript_with_speakers
from .preprocess import preprocess_audio
from .transcribe import transcribe


def run_pipeline(
    file_path: str,
    job_id: str,
    source_filename: str | None = None,
    on_stage: Callable[[str], None] | None = None,
) -> MeetingMinutes:
    """
    Input:
        file_path: path to the raw uploaded meeting audio/video file on disk
            (typically named after job_id, not the user's original filename).
        job_id: id of the job this run belongs to (see app/jobs.py, Phase 2).
        source_filename: the original filename the user uploaded, for display
            purposes. Defaults to file_path's basename if not given.
        on_stage: optional callback invoked with a short stage name
            ("preprocessing", "transcribing", "diarizing", "extracting")
            right before each stage starts, so callers can report progress.
    Output:
        A fully populated, validated MeetingMinutes object.
    """

    def stage(name: str) -> None:
        if on_stage:
            on_stage(name)

    stage("preprocessing")
    cleaned_audio_path = preprocess_audio(file_path)

    stage("transcribing")
    transcript_segments = transcribe(cleaned_audio_path)

    stage("diarizing")
    speaker_segments = diarize(cleaned_audio_path)

    labeled_segments = merge_transcript_with_speakers(transcript_segments, speaker_segments)
    transcript_text = format_transcript_for_llm(labeled_segments)

    stage("extracting")
    minutes = extract_minutes(transcript_text)

    duration_seconds = max((seg["end"] for seg in transcript_segments), default=None)
    participants = list(dict.fromkeys(seg["speaker"] for seg in labeled_segments))

    return MeetingMinutes(
        job_id=job_id,
        source_filename=source_filename or Path(file_path).name,
        generated_at=datetime.now(),
        duration_seconds=duration_seconds,
        summary=minutes.get("summary", ""),
        key_topics=minutes.get("key_topics", []),
        decisions=minutes.get("decisions", []),
        action_items=[ActionItem(**item) for item in minutes.get("action_items", [])],
        transcript=[TranscriptSegment(**seg) for seg in labeled_segments],
        participants=participants,
    )
