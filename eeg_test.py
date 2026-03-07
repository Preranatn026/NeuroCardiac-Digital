import mne
import numpy as np
import pandas as pd
import os

# Path to EEG folder
folder_path = "data/EEG"

files = [f for f in os.listdir(folder_path) if f.endswith(".edf")]

all_rows = []

for file in files:
    print(f"\nProcessing {file} ...")

    file_path = os.path.join(folder_path, file)

    raw = mne.io.read_raw_edf(file_path, preload=True)
    raw.filter(0.5, 45)

    psd = raw.compute_psd(method="welch", fmin=0.5, fmax=45)
    psd_data = psd.get_data()
    freqs = psd.freqs

    bands = {
        "Delta": (0.5, 4),
        "Theta": (4, 8),
        "Alpha": (8, 13),
        "Beta": (13, 30),
        "Gamma": (30, 45)
    }

    row = {"File": file}

    for band, (low, high) in bands.items():
        idx = np.logical_and(freqs >= low, freqs <= high)
        band_power = np.mean(psd_data[:, idx], axis=1)
        row[band] = np.mean(band_power)

    all_rows.append(row)

df = pd.DataFrame(all_rows)
df.to_csv("eeg_features.csv", index=False)

print("\n✅ EEG features extracted for all files!")
print(df)