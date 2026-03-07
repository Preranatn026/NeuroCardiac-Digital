import streamlit as st
import pandas as pd
import numpy as np
import joblib
import time

st.set_page_config(layout="wide")

st.title("🧠❤️ Real-Time NeuroCardiac Digital Twin")

# -----------------------------
# Load Model
# -----------------------------
model = joblib.load("stress_model.pkl")

# -----------------------------
# Session State Initialization
# -----------------------------
if "baseline" not in st.session_state:
    st.session_state.baseline = None

if "history" not in st.session_state:
    st.session_state.history = []

# -----------------------------
# Simulate Incoming Data
# -----------------------------
def simulate_data():
    return {
        "Avg_Heart_Rate": np.random.normal(100, 15),
        "SDNN": np.random.uniform(0.05, 0.2),
        "RMSSD": np.random.uniform(0.05, 0.2),
        "LF_HF_Ratio": np.random.uniform(0.5, 1.5),
        "Beta_Alpha_Ratio": np.random.uniform(0.02, 0.15)
    }

# -----------------------------
# Baseline Calibration
# -----------------------------
if st.button("🔵 Calibrate Baseline"):
    st.session_state.baseline = simulate_data()
    st.success("Baseline Calibrated Successfully!")

# -----------------------------
# Real-Time Loop Simulation
# -----------------------------
placeholder = st.empty()

if st.button("▶ Start Monitoring"):

    for i in range(30):  # simulate 30 time steps
        
        data = simulate_data()
        df_input = pd.DataFrame([data])

        prediction = model.predict(df_input)[0]
        stress_prob = model.predict_proba(df_input).max()

        # Coupling Index
        coupling = data["LF_HF_Ratio"] * data["Beta_Alpha_Ratio"]

        # Stress Score (normalized simple formula)
        stress_index = (
            0.4 * (data["Avg_Heart_Rate"] / 150) +
            0.3 * (data["LF_HF_Ratio"] / 2) +
            0.3 * (data["Beta_Alpha_Ratio"] / 0.2)
        )

        st.session_state.history.append(stress_index)

        with placeholder.container():

            col1, col2, col3 = st.columns(3)

            col1.metric("❤️ Heart Rate", f"{data['Avg_Heart_Rate']:.2f}")
            col2.metric("🧠 LF/HF Ratio", f"{data['LF_HF_Ratio']:.2f}")
            col3.metric("🔗 Coupling Index", f"{coupling:.3f}")

            st.subheader("📊 NeuroCardiac Stress Trend")
            st.line_chart(st.session_state.history)

            # Baseline deviation
            if st.session_state.baseline:
                baseline_hr = st.session_state.baseline["Avg_Heart_Rate"]
                deviation = (data["Avg_Heart_Rate"] - baseline_hr) / baseline_hr
                st.write(f"📌 Deviation from Baseline HR: {deviation*100:.2f}%")

            # Alert System
            if stress_index > 0.8:
                st.error("🚨 CRITICAL NeuroCardiac Instability Detected")
            elif stress_index > 0.6:
                st.warning("⚠ Moderate Risk Detected")
            else:
                st.success("✅ Stable NeuroCardiac State")

            st.write(f"Predicted Stress Level: **{prediction}**")
            st.write(f"Model Confidence: {stress_prob:.2f}")

        time.sleep(2)
