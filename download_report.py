# import io
# import os
# import matplotlib.pyplot as plt
# import streamlit as st

# from hospital_report import build_hospital_pdf

# # ... after you compute `result` and have `patient_name` ...
# fig, ax = plt.subplots(figsize=(10, 3))
# ax.plot(result["Signal"][:2000])
# ax.set_ylim(-3, 3)
# ax.set_title("ECG Waveform")

# buf = io.BytesIO()
# fig.savefig(buf, format="png", dpi=180, bbox_inches="tight")
# ecg_png = buf.getvalue()

# if st.button("📄 Download Hospital Report"):
#     pdf_file = "ECG_Hospital_Report.pdf"
#     build_hospital_pdf(
#         output_path=pdf_file,
#         hospital_name="Your Hospital Name",
#         hospital_address="Address line 1, City, State - PIN | Phone: xxxxx",
#         patient_name=patient_name,
#         patient_id="P000123",
#         age="35",
#         sex="M",
#         doctor_name="Dr. ABC (Cardiology)",
#         test_name="ECG + AI Risk Summary",
#         record_name=record_name,
#         result=result,
#         ecg_plot_png_bytes=ecg_png,
#     )

#     with open(pdf_file, "rb") as f:
#         st.download_button(
#             "⬇ Download PDF",
#             data=f,
#             file_name=pdf_file,
#             mime="application/pdf",
#         )
#     os.remove(pdf_file)