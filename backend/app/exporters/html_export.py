from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.schemas import MeetingMinutes

from .format_utils import format_datetime, format_duration, format_timestamp

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
)


def render_html(minutes: MeetingMinutes) -> str:
    template = _env.get_template("minutes.html")
    return template.render(
        m=minutes,
        generated_display=format_datetime(minutes.generated_at),
        duration_display=format_duration(minutes.duration_seconds),
        format_timestamp=format_timestamp,
    )


def export_html(minutes: MeetingMinutes, output_path: Path) -> Path:
    output_path.write_text(render_html(minutes), encoding="utf-8")
    return output_path
