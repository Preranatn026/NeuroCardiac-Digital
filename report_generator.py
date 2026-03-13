from __future__ import annotations

import io
from datetime import datetime
from typing import Optional, Dict, Any

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors


def build_ecg_report_pdf(
    *,
    output_path: str,
    hospital_name: str,
    report_title: str,
    patient_name: str,
    patient_age: str,
    patient_sex: str,
    patient_id: str,
    sample_test_id: str,
    record_name: str,
    result: Dict[str, Any],
    ecg_plot_png_bytes: bytes,
    hospital_address: str = "",
    hospital_phone: str = "",
    hospital_email: str = "",
    logo_png_bytes: Optional[bytes] = None,
) -> None:
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=30,
        bottomMargin=30,
    )

    elements = []

    # Header
    header_left = []
    header_left.append(Paragraph(f"<b>{report_title}</b>", styles["Title"]))
    header_left.append(Paragraph(f"<b>{hospital_name}</b>", styles["Normal"]))

    contact_line = " | ".join([x for x in [hospital_address, hospital_phone, hospital_email] if x]).strip()
    if contact_line:
        header_left.append(Paragraph(contact_line, styles["Normal"]))

    header_left.append(Paragraph(f"Report Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))

    if logo_png_bytes:
        logo = Image(io.BytesIO(logo_png_bytes), width=1.0 * inch, height=1.0 * inch)
        header_tbl = Table([[header_left, logo]], colWidths=[5.6 * inch, 1.1 * inch])
    else:
        header_tbl = Table([[header_left]], colWidths=[6.7 * inch])

    header_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(header_tbl)
    elements.append(Spacer(1, 0.15 * inch))

    # Patient details
    patient_tbl = Table(
        [
            ["Patient Name", patient_name, "Patient ID", patient_id],
            ["Age", patient_age, "Sex", patient_sex],
            ["Sample/Test ID", sample_test_id, "ECG Record", record_name],
        ],
        colWidths=[1.35 * inch, 2.0 * inch, 1.35 * inch, 2.0 * inch],
    )
    patient_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(patient_tbl)
    elements.append(Spacer(1, 0.2 * inch))

    # ECG image
    elements.append(Paragraph("<b>ECG Waveform (Single Lead)</b>", styles["Heading3"]))
    elements.append(Spacer(1, 0.05 * inch))
    elements.append(Image(io.BytesIO(ecg_plot_png_bytes), width=6.7 * inch, height=2.2 * inch))
    elements.append(Spacer(1, 0.2 * inch))

    # Metrics table
    def g(key: str, default: str = "") -> str:
        v = result.get(key, default)
        if v is None:
            return ""
        if isinstance(v, float):
            return f"{v:.4f}"  # Round float nicely
        return str(v)

    metrics_rows = [
        ["Metric", "Value"],
        ["Average HR (BPM)", g("Average_HR")],
        ["RMSSD", g("RMSSD")],
        ["SDNN", g("SDNN")],
        ["Alpha Power", g("Alpha_Power")],
        ["Beta Power", g("Beta_Power")],
        ["Stress Index", g("Stress_Index")],
        ["Coupling Index", g("Coupling_Index")],
        ["Risk Score", g("Risk_Score")],
        ["Status", g("Status")],
    ]
    metrics_tbl = Table(metrics_rows, colWidths=[3.0 * inch, 3.7 * inch])
    metrics_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaeaea")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    elements.append(Paragraph("<b>Results</b>", styles["Heading3"]))
    elements.append(metrics_tbl)
    elements.append(Spacer(1, 0.2 * inch))

    # Summary
    status = g("Status", "Unknown")
    risk = g("Risk_Score", "NA")
    summary_text = (
        f"Automated ECG analysis completed for record <b>{record_name}</b>. "
        f"Computed risk score is <b>{risk}</b> with status <b>{status}</b>. "
        f"Please correlate clinically."
    )
    elements.append(Paragraph("<b>Summary</b>", styles["Heading3"]))
    elements.append(Paragraph(summary_text, styles["Normal"]))
    elements.append(Spacer(1, 0.25 * inch))

    # Disclaimer
    elements.append(Paragraph(
        "<font size=8 color='grey'>Disclaimer: Computer-generated report for informational use only. "
        "Not a final medical diagnosis.</font>",
        styles["Normal"]
    ))

    doc.build(elements)