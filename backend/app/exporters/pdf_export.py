from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.schemas import MeetingMinutes

from .format_utils import format_datetime, format_duration, format_timestamp

ACCENT = colors.HexColor("#4f46e5")
TEXT = colors.HexColor("#1f2937")
MUTED = colors.HexColor("#6b7280")
BORDER = colors.HexColor("#e5e7eb")
ROW_ALT = colors.HexColor("#f9fafb")


def _e(value: str) -> str:
    """Escape text before handing it to ReportLab's Paragraph, which parses
    a mini-XML markup — unescaped '&'/'<' from LLM output would otherwise
    break rendering or silently drop content."""
    return escape(str(value))


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle("MMTitle", parent=base["Title"], fontSize=24, leading=28,
                                 textColor=ACCENT, alignment=0, spaceAfter=4),
        "meta": ParagraphStyle("MMMeta", parent=base["Normal"], fontSize=9, textColor=MUTED),
        "heading": ParagraphStyle("MMHeading", parent=base["Heading2"], fontSize=13,
                                   textColor=TEXT, spaceBefore=16, spaceAfter=6),
        "body": ParagraphStyle("MMBody", parent=base["Normal"], fontSize=10.5, leading=15, textColor=TEXT),
        "bullet": ParagraphStyle("MMBullet", parent=base["Normal"], fontSize=10.5, leading=15,
                                  leftIndent=14, textColor=TEXT),
        "cell": ParagraphStyle("MMCell", parent=base["Normal"], fontSize=9.5, leading=13, textColor=TEXT),
        "cell_header": ParagraphStyle("MMCellHeader", parent=base["Normal"], fontSize=9.5,
                                       leading=13, textColor=colors.white),
        "speaker": ParagraphStyle("MMSpeaker", parent=base["Normal"], fontSize=9.5, leading=13,
                                   textColor=ACCENT, fontName="Helvetica-Bold"),
        "transcript": ParagraphStyle("MMTranscript", parent=base["Normal"], fontSize=9.5,
                                      leading=13, textColor=colors.HexColor("#374151"), leftIndent=8),
    }
    return styles


def export_pdf(minutes: MeetingMinutes, output_path: Path) -> Path:
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )
    s = _styles()
    story = []

    story.append(Paragraph("Meeting Minutes", s["title"]))
    meta_parts = [_e(minutes.source_filename), f"Generated {format_datetime(minutes.generated_at)}"]
    if minutes.duration_seconds:
        meta_parts.append(f"Duration {format_duration(minutes.duration_seconds)}")
    story.append(Paragraph(" &nbsp;&middot;&nbsp; ".join(meta_parts), s["meta"]))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Summary", s["heading"]))
    story.append(Paragraph(_e(minutes.summary) or "No summary available.", s["body"]))

    if minutes.key_topics:
        story.append(Paragraph("Key Topics", s["heading"]))
        story.append(Paragraph(" &nbsp;&bull;&nbsp; ".join(_e(t) for t in minutes.key_topics), s["body"]))

    if minutes.decisions:
        story.append(Paragraph("Decisions", s["heading"]))
        for d in minutes.decisions:
            story.append(Paragraph(f"&#10003; {_e(d)}", s["bullet"]))

    if minutes.action_items:
        story.append(Paragraph("Action Items", s["heading"]))
        table_data = [[
            Paragraph("Task", s["cell_header"]),
            Paragraph("Owner", s["cell_header"]),
            Paragraph("Deadline", s["cell_header"]),
        ]]
        for item in minutes.action_items:
            table_data.append([
                Paragraph(_e(item.task), s["cell"]),
                Paragraph(_e(item.owner), s["cell"]),
                Paragraph(_e(item.deadline), s["cell"]),
            ])
        table = Table(table_data, colWidths=[3.3 * inch, 1.4 * inch, 1.4 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW_ALT]),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(table)

    if minutes.participants:
        story.append(Paragraph("Participants", s["heading"]))
        story.append(Paragraph(", ".join(_e(p) for p in minutes.participants), s["body"]))

    if minutes.transcript:
        story.append(Paragraph("Full Transcript", s["heading"]))
        for seg in minutes.transcript:
            story.append(Paragraph(f"{format_timestamp(seg.start)} &nbsp; {_e(seg.speaker)}", s["speaker"]))
            story.append(Paragraph(_e(seg.text), s["transcript"]))
            story.append(Spacer(1, 4))

    doc.build(story)
    return output_path
