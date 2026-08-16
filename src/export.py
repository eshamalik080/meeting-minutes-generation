import json
from datetime import datetime


def export_json(minutes: dict, output_path: str = "outputs/minutes.json") -> str:
    with open(output_path, "w") as f:
        json.dump(minutes, f, indent=2)
    return output_path


def export_html(minutes: dict, output_path: str = "outputs/minutes.html") -> str:
    action_items_html = "".join(
        f"<li><b>{item['task']}</b> — owner: {item['owner']}, deadline: {item['deadline']}</li>"
        for item in minutes.get("action_items", [])
    )
    topics_html = "".join(f"<li>{t}</li>" for t in minutes.get("key_topics", []))
    decisions_html = "".join(f"<li>{d}</li>" for d in minutes.get("decisions", []))

    html = f"""<!DOCTYPE html>
<html>
<head><title>Meeting Minutes</title></head>
<body>
<h1>Meeting Minutes</h1>
<p><i>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</i></p>

<h2>Summary</h2>
<p>{minutes.get('summary', '')}</p>

<h2>Key Topics</h2>
<ul>{topics_html}</ul>

<h2>Decisions</h2>
<ul>{decisions_html}</ul>

<h2>Action Items</h2>
<ul>{action_items_html}</ul>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)
    return output_path


def export_pdf(minutes: dict, output_path: str = "outputs/minutes.pdf") -> str:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Meeting Minutes", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Summary", styles["Heading2"]))
    story.append(Paragraph(minutes.get("summary", ""), styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Key Topics", styles["Heading2"]))
    for topic in minutes.get("key_topics", []):
        story.append(Paragraph(f"• {topic}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Decisions", styles["Heading2"]))
    for decision in minutes.get("decisions", []):
        story.append(Paragraph(f"• {decision}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Action Items", styles["Heading2"]))
    for item in minutes.get("action_items", []):
        story.append(Paragraph(
            f"• {item['task']} — owner: {item['owner']}, deadline: {item['deadline']}",
            styles["Normal"]
        ))

    doc.build(story)
    return output_path


def export_all_formats(minutes: dict, output_dir: str = "outputs") -> dict:
    return {
        "json": export_json(minutes, f"{output_dir}/minutes.json"),
        "html": export_html(minutes, f"{output_dir}/minutes.html"),
        "pdf": export_pdf(minutes, f"{output_dir}/minutes.pdf"),
    }


if __name__ == "__main__":
    sample_minutes = {
        "summary": "Test meeting about project deadlines.",
        "key_topics": ["deadlines", "budget"],
        "decisions": ["Approved Q3 budget"],
        "action_items": [{"task": "Send report", "owner": "Esha", "deadline": "Friday"}]
    }
    paths = export_all_formats(sample_minutes)
    print("Exported files:", paths)
