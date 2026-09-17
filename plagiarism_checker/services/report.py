"""Build a PDF summary of a plagiarism-check run."""

from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

def build_pdf_report(output_path, filename, overall_percent, risk_level, matches):
    doc = SimpleDocTemplate(output_path, pagesize = letter)
    styles = getSampleStyleSheet()
    file = []

    file.append(Paragraph("Plagiarism Check Report", styles["Title"]))
    file.append(Spacer(1, 12))
    file.append(Paragraph(f"<b>Document:</b> {escape(filename)}", styles["Normal"]))
    file.append(Paragraph(f"<b>Overall similarity:</b> {overall_percent}%", styles["Normal"]))
    file.append(Paragraph(f"<b>Risk level:</b> {escape(risk_level)}", styles["Normal"]))
    file.append(Spacer(1, 20))

    file.append(Paragraph("Matched Phrases", styles["Heading2"]))

    if not matches:
        file.append(Spacer(1, 8))
        file.append(Paragraph("No matches were found above the similarity threshold.", styles["Normal"]))
    else:
        for m in matches:
            file.append(Spacer(1, 12))
            file.append(Paragraph(f"<b>Phrase:</b> {escape(m['phrase'])}", styles["Normal"]))
            file.append(Paragraph(f"<b>Similarity:</b> {m['similarity']}%", styles["Normal"]))
            url = escape(m["url"])
            file.append(Paragraph(f"<b>Source:</b> <link href='{url}'>{url}</link>", styles["Normal"]))
            if m.get("snippet"):
                file.append(Paragraph(f"<b>Matched text:</b> <i>{escape(m['snippet'])}</i>", styles["Normal"]))

    doc.build(file)
    return output_path