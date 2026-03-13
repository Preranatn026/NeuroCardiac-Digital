# """
# Hospital-style PDF report generator for your Streamlit app.

# What it does:
# - Creates a professional-looking PDF similar to hospital test reports:
#   - Hospital header
#   - Patient details section (name, age, sex, patient id, date/time)
#   - Test details (ECG record id)
#   - ECG plot image
#   - Results table (HR, RMSSD, SDNN, etc.)
#   - Interpretation / Summary paragraph
#   - Signature line

# How to use:
# - Copy `build_hospital_pdf(...)` into your repo (for example: report_generator.py)
# - Call it from app.py when user clicks "Download report"
# """

# from __future__ import annotations

# import io
# from datetime import datetime
# from reportlab.platypus import (
#     SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
# )
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.lib.units import inch
# from reportlab.lib import colors


# def build_hospital_pdf(
#     *,
#     output_path: str,
#     hospital_name: str,
#     hospital_address: str,
#     patient_name: str,
#     patient_id: str,
#     age: str,
#     sex: str,
#     doctor_name: str,
#     test_name: str,
#     record_name: str,
#     result: dict,
#     ecg_plot_png_bytes: bytes,
# ) -> None:
#     """
#     Creates a hospital-style ECG report PDF.

#     output_path: where to save pdf
#     result: dict returned by analyze_ecg() (must contain keys used below)
#     ecg_plot_png_bytes: PNG image bytes of ECG plot (matplotlib saved to bytes)
#     """
#     styles = getSampleStyleSheet()
#     doc = SimpleDocTemplate(output_path, pagesize=A4,
#                             leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)

#     elements = []

#     # -----------------------
#     # Header
#     # -----------------------
#     elements.append(Paragraph(f"<b>{hospital_name}</b>", styles["Title"]))
#     elements.append(Paragraph(hospital_address, styles["Normal"]))
#     elements.append(Spacer(1, 0.15 * inch))

#     now = datetime.now().strftime("%Y-%m-%d %H:%M")
#     elements.append(Paragraph(f"<b>Report Date/Time:</b> {now}", styles["Normal"]))
#     elements.append(Spacer(1, 0.15 * inch))

#     # -----------------------
#     # Patient details box
#     # -----------------------
#     patient_table = Table(
#         [
#             ["Patient Name", patient_name, "Patient ID", patient_id],
#             ["Age", age, "Sex", sex],
#             ["Referred By", doctor_name, "Test", test_name],
#             ["ECG Record", record_name, "Status", str(result.get("Status", ""))],
#         ],
#         colWidths=[1.2*inch, 2.1*inch, 1.2*inch, 2.0*inch]
#     )
#     patient_table.setStyle(TableStyle([
#         ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
#         ("BOX", (0, 0), (-1, -1), 1, colors.black),
#         ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
#         ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
#         ("FONTSIZE", (0, 0), (-1, -1), 9),
#         ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
#         ("LEFTPADDING", (0, 0), (-1, -1), 6),
#         ("RIGHTPADDING", (0, 0), (-1, -1), 6),
#         ("TOPPADDING", (0, 0), (-1, -1), 4),
#         ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
#     ]))
#     elements.append(patient_table)
#     elements.append(Spacer(1, 0.2 * inch))

#     # -----------------------
#     # ECG Image
#     # -----------------------
#     elements.append(Paragraph("<b>ECG Waveform</b>", styles["Heading3"]))
#     img_buf = io.BytesIO(ecg_plot_png_bytes)
#     ecg_img = Image(img_buf, width=6.7*inch, height=2.2*inch)
#     elements.append(ecg_img)
#     elements.append(Spacer(1, 0.2 * inch))

#     # -----------------------
#     # Results table
#     # -----------------------
#     elements.append(Paragraph("<b>Results</b>", styles["Heading3"]))

#     rows = [
#         ["Parameter", "Value", "Reference (Example)"],
#         ["Heart Rate (BPM)", str(result.get("Average_HR", "")), "60–100"],
#         ["RMSSD", str(result.get("RMSSD", "")), "20–100 (varies)"],
#         ["SDNN", str(result.get("SDNN", "")), "50–100 (varies)"],
#         ["Alpha Power", str(result.get("Alpha_Power", "")), "—"],
#         ["Beta Power", str(result.get("Beta_Power", "")), "—"],
#         ["Stress Index", str(result.get("Stress_Index", "")), "Lower is better"],
#         ["Coupling Index", str(result.get("Coupling_Index", "")), "—"],
#         ["Risk Score", str(result.get("Risk_Score", "")), "0–100"],
#         ["AI/ML Status", str(result.get("Status", "")), "Normal/At Risk"],
#     ]

#     results_table = Table(rows, colWidths=[2.2*inch, 1.3*inch, 3.2*inch])
#     results_table.setStyle(TableStyle([
#         ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaeaea")),
#         ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
#         ("BOX", (0, 0), (-1, -1), 1, colors.black),
#         ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.grey),
#         ("FONTSIZE", (0, 0), (-1, -1), 9),
#         ("LEFTPADDING", (0, 0), (-1, -1), 6),
#         ("RIGHTPADDING", (0, 0), (-1, -1), 6),
#         ("TOPPADDING", (0, 0), (-1, -1), 4),
#         ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
#     ]))
#     elements.append(results_table)
#     elements.append(Spacer(1, 0.2 * inch))

#     # -----------------------
#     # Interpretation / Summary
#     # -----------------------
#     elements.append(Paragraph("<b>Interpretation</b>", styles["Heading3"]))

#     status = str(result.get("Status", ""))
#     risk = str(result.get("Risk_Score", ""))

#     interpretation = (
#         f"This report is generated using an automated analysis system. "
#         f"ECG record: <b>{record_name}</b>. "
#         f"Computed risk score: <b>{risk}</b>. "
#         f"Status: <b>{status}</b>. "
#         f"Please correlate clinically and confirm with a cardiologist."
#     )
#     elements.append(Paragraph(interpretation, styles["Normal"]))
#     elements.append(Spacer(1, 0.35 * inch))

#     # -----------------------
#     # Signature block
#     # -----------------------
#     elements.append(Paragraph("______________________________", styles["Normal"]))
#     elements.append(Paragraph(f"Authorized Signatory / Doctor: {doctor_name}", styles["Normal"]))
#     elements.append(Spacer(1, 0.05 * inch))
#     elements.append(Paragraph("<font size=8 color='grey'>This is a computer-generated report.</font>", styles["Normal"]))

#     doc.build(elements)