"""
In-memory job store. Good enough for a single-process dev/demo deployment
(Phase 7 target: one Render/Railway instance). If this ever needs to run
across multiple worker processes, swap this for something shared (Redis,
a DB row) — the JobStore interface below is the seam to do that at.
"""

import threading
from dataclasses import dataclass, field
from datetime import datetime

from app.schemas import JobStatus, MeetingMinutes


@dataclass
class Job:
    job_id: str
    filename: str
    status: JobStatus = JobStatus.PENDING
    stage: str | None = None
    error: str | None = None
    result: MeetingMinutes | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(self, job_id: str, filename: str) -> Job:
        job = Job(job_id=job_id, filename=filename)
        with self._lock:
            self._jobs[job_id] = job
        return job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def set_stage(self, job_id: str, stage: str) -> None:
        self._update(job_id, status=JobStatus.PROCESSING, stage=stage)

    def mark_completed(self, job_id: str, result: MeetingMinutes) -> None:
        self._update(job_id, status=JobStatus.COMPLETED, stage=None, result=result)

    def mark_failed(self, job_id: str, error: str) -> None:
        self._update(job_id, status=JobStatus.FAILED, stage=None, error=error)

    def _update(self, job_id: str, **fields) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return
            for key, value in fields.items():
                setattr(job, key, value)
            job.updated_at = datetime.now()


job_store = JobStore()
