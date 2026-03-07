import wfdb
import numpy as np
import pandas as pd
import os
from scipy.signal import find_peaks

folder_path = "data/ECG"

records = [f.split(".")[0] for f in os.listdir(folder_path) if f.endswith(".dat")]

rows = []

for record in records:
    print(f"Processing {record}...")

    record_path = os.path.join(folder_path, record)

    signal, fields = wfdb.rdsamp(record_path)
    ecg_signal = signal[:, 0]   # take first channel
    sampling_rate = fields["fs"]

    # Normalize
    ecg_signal = (ecg_signal - np.mean(ecg_signal)) / np.std(ecg_signal)

    # Detect peaks
    peaks, _ = find_peaks(ecg_signal, distance=sampling_rate*0.4)

    if len(peaks) < 10:
        continue

    rr_intervals = np.diff(peaks) / sampling_rate

    heart_rate = 60 / np.mean(rr_intervals)
    sdnn = np.std(rr_intervals)
    rmssd = np.sqrt(np.mean(np.square(np.diff(rr_intervals))))
    lf_hf_ratio = sdnn / (rmssd + 1e-6)

    rows.append({
        "Record": record,
        "Avg_Heart_Rate": heart_rate,
        "SDNN": sdnn,
        "RMSSD": rmssd,
        "LF_HF_Ratio": lf_hf_ratio
    })

ecg_df = pd.DataFrame(rows)
ecg_df.to_csv("ecg_features.csv", index=False)

print("✅ ECG Features Extracted")
print(ecg_df)