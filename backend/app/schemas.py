"""
The Meeting Minutes data contract — assembled in ml_pipeline/pipeline.py,
served by the API (Phase 2), rendered by the frontend, and written out by
the exporters (Phase 3). This is the one shape every other part of the
system agrees on.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ActionItem(BaseModel):
    task: str
    owner: str = "unknown"
    deadline: str = "unknown"


class TranscriptSegment(BaseModel):
    start: float = Field(description="Segment start time in seconds")
    end: float = Field(description="Segment end time in seconds")
    speaker: str
    text: str


class MeetingMinutes(BaseModel):
    job_id: str
    source_filename: str
    generated_at: datetime
    duration_seconds: float | None = None

    summary: str
    key_topics: list[str] = Field(default_factory=list)
    decisions: list[str] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)

    transcript: list[TranscriptSegment] = Field(default_factory=list)
    participants: list[str] = Field(default_factory=list)


class UploadResponse(BaseModel):
    job_id: str
    status: JobStatus


class StatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    filename: str
    stage: str | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime
