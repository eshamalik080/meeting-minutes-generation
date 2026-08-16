"""Shared formatting helpers used by both the HTML and PDF exporters."""

from datetime import datetime


def format_duration(seconds: float | None) -> str:
    if seconds is None:
        return "Unknown"
    total = int(seconds)
    m, s = divmod(total, 60)
    return f"{m}m {s}s"


def format_timestamp(seconds: float) -> str:
    total = int(seconds)
    m, s = divmod(total, 60)
    return f"{m:02d}:{s:02d}"


def format_datetime(dt: datetime) -> str:
    return dt.strftime("%B %d, %Y at %H:%M")
