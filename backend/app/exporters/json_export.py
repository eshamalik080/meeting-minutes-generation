from pathlib import Path

from app.schemas import MeetingMinutes


def export_json(minutes: MeetingMinutes, output_path: Path) -> Path:
    output_path.write_text(minutes.model_dump_json(indent=2), encoding="utf-8")
    return output_path
