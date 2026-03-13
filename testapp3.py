import streamlit as st
import matplotlib.pyplot as plt
import time
import os
import io
import glob
import wfdb
import mne

from ecg_processing import analyze_ecg
from report_generator import build_ecg_report_pdf

st.set_page_config(page_title="NeuroCardiac AI Twin", layout="wide")

# ---------- DARK THEME ----------
st.markdown("""
<style>
body {background-color:#0e1117;color:white;}
div[data-testid="metric-container"]{
background-color:#1c1f26;border-radius:15px;padding:15px;
box-shadow:0px 0px 12px rgba(0,255,255,0.3);}
div[data-testid="metric-container"] label{
color:#00FFFF !important;font-weight:bold;}
div[data-testid="metric-container"] div{
color:#FFFFFF !important;font-size:28px !important;font-weight:bold;}
.stButton>button{
background-color:#00FFFF;color:black;border-radius:10px;font-weight:bold;}
</style>
""", unsafe_allow_html=True)

st.title("🧠❤️ NeuroCardiac AI Digital Twin")
st.markdown("### Real-Time Brain–Heart Intelligence System")

# ---------------- Patient Inputs ----------------
st.subheader("🧾 Patient Details")
c1, c2, c3 = st.columns(3)
patient_name = c1.text_input("Patient Name *")
patient_age = c2.text_input("Age *", placeholder="e.g. 35")
patient_sex = c3.selectbox("Sex *", ["Male", "Female", "Other"])

c4, c5 = st.columns(2)
patient_id = c4.text_input("Patient ID *", placeholder="e.g. P0001")
sample_test_id = c5.text_input("Sample/Test ID *", placeholder="e.g. ECG-2026-001")

# ---------------- EEG INPUT ----------------
st.subheader("🧠 EEG Input (Existing Records)")
if not os.path.exists("eeg_data"):
    os.makedirs("eeg_data")
eeg_files = glob.glob("eeg_data/*.edf")
eeg_names = ["Demo_EEG"] if len(eeg_files) == 0 else [os.path.splitext(os.path.basename(f))[0] for f in eeg_files]
eeg_record_name = st.selectbox("Select EEG Record", eeg_names)

# ---------------- ECG INPUT ----------------
st.subheader("📥 ECG Input (Existing Records)")
available_records = sorted({os.path.splitext(f)[0] for f in glob.glob("*.hea")})
available_records = ["100","101"] if not available_records else available_records
record_name = st.selectbox("Select ECG Record", available_records)

# ---------------- Session State ----------------
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None
if "analysis_record" not in st.session_state:
    st.session_state["analysis_record"] = None

# ---------------- Analyze ----------------
if st.button("Activate Digital Twin"):
    required = {
        "Patient Name": patient_name,
        "Age": patient_age,
        "Patient ID": patient_id,
        "Sample/Test ID": sample_test_id,
    }
    missing = [k for k,v in required.items() if not str(v).strip()]
    if missing:
        st.warning("Please fill required fields: " + ", ".join(missing))
        st.stop()

    try:
        # ---------- Load ECG ----------
        record = wfdb.rdrecord(record_name)
        ecg_signal = record.p_signal[:,0]
        fs = record.fs

        # ---------- Load EEG ----------
        if eeg_record_name == "Demo_EEG":
            eeg_signal = ecg_signal[:5000]
        else:
            eeg_file_path = f"eeg_data/{eeg_record_name}.edf"
            eeg_raw = mne.io.read_raw_edf(eeg_file_path, preload=True)
            eeg_signal = eeg_raw.get_data()[0]

        # Save EEG to session state for later PDF use
        st.session_state["eeg_signal"] = eeg_signal

        # ---------- Monitoring Simulation ----------
        status_text = st.empty()
        progress_bar = st.progress(0)
        for i in range(3):
            status_text.write(f"Monitoring cardiac-neural signals... {i+1}/3")
            progress_bar.progress((i+1)*33)
            time.sleep(1)
        status_text.write("Monitoring complete ✅")

        # ---------- Run Analysis ----------
        result = analyze_ecg(ecg_signal, eeg_signal, fs=fs)

        # Generate EEG plot for PDF
        eeg_window = min(2000, len(eeg_signal))
        fig_eeg, ax_eeg = plt.subplots(figsize=(10,3))
        ax_eeg.plot(eeg_signal[:eeg_window])
        ax_eeg.set_title(f"EEG Signal - Record {record_name}")
        img_buf_eeg = io.BytesIO()
        fig_eeg.savefig(img_buf_eeg, format="png", dpi=180, bbox_inches="tight")
        result["EEG_Plot"] = img_buf_eeg.getvalue()

        # Save result and patient info to session state
        st.session_state["analysis_result"] = result
        st.session_state["analysis_record"] = record_name
        st.session_state["patient_name"] = patient_name.strip()
        st.session_state["patient_age"] = patient_age.strip()
        st.session_state["patient_sex"] = patient_sex
        st.session_state["patient_id"] = patient_id.strip()
        st.session_state["sample_test_id"] = sample_test_id.strip()

    except Exception as e:
        st.error(f"Analysis failed for record {record_name}. Error: {e}")
        st.stop()

# ---------------- Display Metrics ----------------
result = st.session_state.get("analysis_result")
analysis_record = st.session_state.get("analysis_record")

if result:
    # Cardiac Metrics
    st.subheader("🩺 Cardiac Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Heart Rate (BPM)", result["Average_HR"])
    col2.metric("RMSSD", result["RMSSD"])
    col3.metric("SDNN", result["SDNN"])

    # EEG Metrics
    st.subheader("🧠 EEG Metrics")
    col4, col5, col6 = st.columns(3)
    col4.metric("Alpha Power", result["Alpha_Power"])
    col5.metric("Beta Power", result["Beta_Power"])
    col6.metric("Stress Index", result["Stress_Index"])

    # AI Risk
    st.subheader("🔗 AI Risk Intelligence")
    col7, col8 = st.columns(2)
    col7.metric("Coupling Index", result["Coupling_Index"])
    col8.metric("ML Status", result["Status"])
    st.progress(min(int(result["Risk_Score"]), 100))

    # Signal Plots
    st.subheader("🧠❤️ Brain–Heart Signal Twin")
    col_ecg, col_eeg = st.columns(2)
    with col_ecg:
        sig = result["Signal"]
        window = min(2000, len(sig))
        fig1, ax1 = plt.subplots(figsize=(6,3))
        ax1.plot(sig[:window])
        ax1.set_title("ECG Signal")
        st.pyplot(fig1)
    with col_eeg:
        eeg_signal = st.session_state.get("eeg_signal", [])
        eeg_window = min(2000, len(eeg_signal))
        fig2, ax2 = plt.subplots(figsize=(6,3))
        ax2.plot(eeg_signal[:eeg_window])
        ax2.set_title("EEG Signal")
        st.pyplot(fig2)

    st.success("🧠 Digital Twin Fully Activated")

# ---------------- Download Report ----------------
st.subheader("📄 Patient Report (Download)")

if result is None:
    st.info("Run 'Activate Digital Twin' first to generate the report.")
else:
    # retrieve EEG signal safely
    eeg_signal = st.session_state.get("eeg_signal", [])

    # generate ECG plot for PDF
    sig = result["Signal"]
    window = min(2000, len(sig))
    fig_ecg, ax_ecg = plt.subplots(figsize=(10,3))
    ax_ecg.plot(sig[:window])
    ax_ecg.set_ylim(-3,3)
    ax_ecg.set_title(f"ECG Waveform - Record {analysis_record}")
    img_buf_ecg = io.BytesIO()
    fig_ecg.savefig(img_buf_ecg, format="png", dpi=180, bbox_inches="tight")
    ecg_png_bytes = img_buf_ecg.getvalue()

    # generate EEG plot for PDF
    if len(eeg_signal) > 0:
        eeg_window = min(2000, len(eeg_signal))
        fig_eeg, ax_eeg = plt.subplots(figsize=(10,3))
        ax_eeg.plot(eeg_signal[:eeg_window])
        ax_eeg.set_title(f"EEG Signal - Record {analysis_record}")
        img_buf_eeg = io.BytesIO()
        fig_eeg.savefig(img_buf_eeg, format="png", dpi=180, bbox_inches="tight")
        result["EEG_Plot"] = img_buf_eeg.getvalue()

    if st.button("⬇ Download ECG Report"):
        safe_name = (st.session_state.get("patient_name", "Patient")).replace(" ","_")
        pdf_file = f"{safe_name}_ECG_Report.pdf"

        build_ecg_report_pdf(
            output_path=pdf_file,
            hospital_name="AI Analyzation",
            report_title="ECG Report",
            patient_name=st.session_state.get("patient_name",""),
            patient_age=st.session_state.get("patient_age",""),
            patient_sex=st.session_state.get("patient_sex",""),
            patient_id=st.session_state.get("patient_id",""),
            sample_test_id=st.session_state.get("sample_test_id",""),
            record_name=analysis_record,
            result=result,
            ecg_plot_png_bytes=ecg_png_bytes,
            hospital_address="",
            hospital_phone="",
            hospital_email="",
            logo_png_bytes=None,
        )

        with open(pdf_file,"rb") as f:
            st.download_button(
                label="⬇ Click here to download PDF",
                data=f,
                file_name=pdf_file,
                mime="application/pdf",
            )
        os.remove(pdf_file)