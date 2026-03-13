from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
import io


def build_ecg_report_pdf(
    output_path,
    hospital_name,
    report_title,
    patient_name,
    patient_age,
    patient_sex,
    patient_id,
    sample_test_id,
    record_name,
    result,
    ecg_plot_png_bytes,
    hospital_address="",
    hospital_phone="",
    hospital_email="",
    logo_png_bytes=None,
):

    styles = getSampleStyleSheet()
    story = []

    # ---------- TITLE ----------
    story.append(Paragraph("<b>NeuroCardiac Digital Twin Report</b>", styles["Title"]))
    story.append(Spacer(1, 20))

    # ---------- PATIENT DETAILS TABLE ----------
    story.append(Paragraph("<b>Patient Details</b>", styles["Heading2"]))

    patient_data = [
        ["Patient Name", patient_name],
        ["Patient ID", patient_id],
        ["Age", patient_age],
        ["Sex", patient_sex],
        ["Sample/Test ID", sample_test_id],
        ["Record Name", record_name],
    ]

    patient_table = Table(patient_data, colWidths=[200, 300])

    patient_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.lightgrey),
    ]))

    story.append(patient_table)
    story.append(Spacer(1, 25))

    # ---------- ECG GRAPH ----------
    story.append(Paragraph("<b>ECG Signal (Heart Activity)</b>", styles["Heading2"]))

    ecg_img = Image(io.BytesIO(ecg_plot_png_bytes))
    ecg_img.drawHeight = 2.5 * inch
    ecg_img.drawWidth = 6 * inch

    story.append(ecg_img)
    story.append(Spacer(1, 25))

    # ---------- EEG GRAPH ----------
    if "EEG_Plot" in result:

        story.append(Paragraph("<b>EEG Signal (Brain Activity)</b>", styles["Heading2"]))

        eeg_img = Image(io.BytesIO(result["EEG_Plot"]))
        eeg_img.drawHeight = 2.5 * inch
        eeg_img.drawWidth = 6 * inch

        story.append(eeg_img)
        story.append(Spacer(1, 25))

    # ---------- NEUROCARDIAC VALUES TABLE ----------
    story.append(Paragraph("<b>NeuroCardiac Digital Twin Values</b>", styles["Heading2"]))

    values_data = [
        ["ECG Heart Rate (BPM)", result.get("Average_HR", "N/A")],
        ["EEG Alpha Power", result.get("Alpha_Power", "N/A")],
        ["EEG Beta Power", result.get("Beta_Power", "N/A")],
        ["Stress Index", result.get("Stress_Index", "N/A")],
        ["Coupling Index", result.get("Coupling_Index", "N/A")],
        ["Risk Score", result.get("Risk_Score", "N/A")],
        ["AI Status", result.get("Status", "N/A")],
    ]

    values_table = Table(values_data, colWidths=[250, 250])

    values_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.lightgrey),
    ]))

    story.append(values_table)
    story.append(Spacer(1, 25))

    # ---------- SHORT SUMMARY ----------
    story.append(Paragraph("<b>Health Summary</b>", styles["Heading2"]))

    summary_text = f"""
    ECG and EEG signals were analyzed using the NeuroCardiac Digital Twin system.

    Heart Rate: {result.get("Average_HR","N/A")} BPM  
    Alpha Power: {result.get("Alpha_Power","N/A")}  
    Beta Power: {result.get("Beta_Power","N/A")}  

    Coupling Index: {result.get("Coupling_Index","N/A")}  
    Risk Score: {result.get("Risk_Score","N/A")}  
    Status: {result.get("Status","N/A")}
    """

    story.append(Paragraph(summary_text, styles["Normal"]))

    # ---------- BUILD PDF ----------
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    doc.build(story)
