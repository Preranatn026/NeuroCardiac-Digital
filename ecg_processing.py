import numpy as np
from scipy.signal import find_peaks
import mne

def analyze_ecg(ecg_signal, eeg_signal, fs=250):
    """
    Analyze ECG and EEG signals for NeuroCardiac Digital Twin.

    Args:
        ecg_signal: 1D numpy array of ECG samples
        eeg_signal: 1D numpy array of EEG samples
        fs: ECG sampling frequency in Hz (default 250)

    Returns:
        dict with:
        - Average_HR, RMSSD, SDNN
        - Alpha_Power, Beta_Power, Stress_Index
        - Coupling_Index, Risk_Score, Status
    """

    # ---------- ECG Analysis ----------
    ecg_signal = np.array(ecg_signal)
    peaks, _ = find_peaks(ecg_signal, distance=fs*0.6)  # min 0.6s between beats
    rr_intervals = np.diff(peaks)

    if len(rr_intervals) == 0:
        rr_intervals = np.array([1])

    rr_intervals_sec = rr_intervals / fs

    # Heart Rate & HRV
    average_hr = 60 / np.mean(rr_intervals_sec)
    rmssd = np.sqrt(np.mean(np.square(np.diff(rr_intervals_sec))))
    sdnn = np.std(rr_intervals_sec)

    # ---------- EEG Analysis ----------
    eeg_signal = np.array(eeg_signal)
    n = len(eeg_signal)
    freqs = np.fft.rfftfreq(n, d=1/fs)
    fft_vals = np.abs(np.fft.rfft(eeg_signal))**2

    # Power in standard bands
    alpha_power = fft_vals[(freqs >= 8) & (freqs <= 12)].mean() + 1e-6
    beta_power = fft_vals[(freqs >= 13) & (freqs <= 30)].mean() + 1e-6

    stress_index = beta_power / alpha_power

    # ---------- Brain-Heart Coupling ----------
    coupling_index = (rmssd + sdnn) / (alpha_power + beta_power + 1e-6)

    # ---------- Risk Score ----------
    risk_score = min(100, stress_index * 50)
    status = "Stable"
    if risk_score > 60:
        status = "High Risk"
    elif risk_score > 30:
        status = "Moderate Risk"

    return {
        "Average_HR": round(average_hr, 2),
        "RMSSD": round(rmssd, 4),
        "SDNN": round(sdnn, 4),
        "Alpha_Power": round(alpha_power, 4),
        "Beta_Power": round(beta_power, 4),
        "Stress_Index": round(stress_index, 4),
        "Coupling_Index": round(coupling_index, 4),
        "Risk_Score": int(risk_score),
        "Status": status,
        "Signal": ecg_signal
    }