"""
/upload, /status/{job_id}, /result/{job_id}.

Upload streams the file to disk in chunks (so large meeting recordings
don't sit fully in memory), then hands off to a FastAPI BackgroundTask —
process_job() is a plain sync function, so Starlette runs it in a
threadpool automatically and the request returns immediately with a job_id.
"""

import logging
from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.config import ALLOWED_EXTENSIONS, MAX_UPLOAD_BYTES, MAX_UPLOAD_MB, UPLOAD_CHUNK_SIZE, UPLOADS_DIR
from app.jobs import job_store
from app.schemas import JobStatus, MeetingMinutes, StatusResponse, UploadResponse
from ml_pipeline.pipeline import run_pipeline

logger = logging.getLogger("app.api")

router = APIRouter()


def process_job(job_id: str, file_path: str, source_filename: str) -> None:
    try:
        minutes = run_pipeline(
            file_path,
            job_id=job_id,
            source_filename=source_filename,
            on_stage=lambda stage: job_store.set_stage(job_id, stage),
        )
        job_store.mark_completed(job_id, minutes)
    except Exception as exc:
        logger.exception("Pipeline failed for job %s", job_id)
        job_store.mark_failed(job_id, str(exc))


@router.post("/upload", response_model=UploadResponse, status_code=202)
async def upload_meeting(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "No filename provided.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            400,
            f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    job_id = str(uuid4())
    dest_path = UPLOADS_DIR / f"{job_id}{ext}"

    size = 0
    try:
        async with aiofiles.open(dest_path, "wb") as out:
            while chunk := await file.read(UPLOAD_CHUNK_SIZE):
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    raise HTTPException(413, f"File exceeds {MAX_UPLOAD_MB}MB limit.")
                await out.write(chunk)
    except HTTPException:
        dest_path.unlink(missing_ok=True)
        raise
    except OSError as exc:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(500, f"Failed to save upload: {exc}") from exc

    job_store.create(job_id=job_id, filename=file.filename)
    background_tasks.add_task(process_job, job_id, str(dest_path), file.filename)

    return UploadResponse(job_id=job_id, status=JobStatus.PENDING)


@router.get("/status/{job_id}", response_model=StatusResponse)
def get_status(job_id: str):
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(404, "Job not found.")
    return StatusResponse(
        job_id=job.job_id,
        status=job.status,
        filename=job.filename,
        stage=job.stage,
        error=job.error,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.get("/result/{job_id}", response_model=MeetingMinutes)
def get_result(job_id: str):
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(404, "Job not found.")
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(409, f"Job is not completed yet (status: {job.status.value}).")
    return job.result
