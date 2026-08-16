"""
Phase 1 sanity check — runs the full mocked pipeline and prints the
resulting MeetingMinutes object. Run from backend/ with the venv active:

    python test_pipeline.py

No real audio file is required: preprocess_audio()'s mock creates a
placeholder if the given path doesn't exist, since every mock stage
downstream ignores the actual audio content anyway.
"""

import json

from ml_pipeline.pipeline import run_pipeline

if __name__ == "__main__":
    minutes = run_pipeline("storage/uploads/sample_meeting.mp3", job_id="test-job-001")

    print("=== MeetingMinutes (validated Pydantic model) ===")
    print(json.dumps(minutes.model_dump(mode="json"), indent=2))

    assert minutes.summary, "summary should not be empty"
    assert len(minutes.transcript) > 0, "transcript should have segments"
    assert len(minutes.action_items) > 0, "action_items should not be empty"
    assert len(minutes.participants) >= 2, "expected multiple speakers"

    print("\nAll checks passed.")
