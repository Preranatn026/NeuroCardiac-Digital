import pandas as pd
import numpy as np

# Load feature files
ecg_df = pd.read_csv("ecg_features.csv")
eeg_df = pd.read_csv("eeg_features.csv")

print("ECG rows:", len(ecg_df))
print("EEG rows:", len(eeg_df))

# ---------------------------
# Match row counts safely
# ---------------------------

if len(ecg_df) < len(eeg_df):
    repeats = int(np.ceil(len(eeg_df) / len(ecg_df)))
    ecg_df = pd.concat([ecg_df] * repeats, ignore_index=True)
    ecg_df = ecg_df.iloc[:len(eeg_df)]

elif len(eeg_df) < len(ecg_df):
    repeats = int(np.ceil(len(ecg_df) / len(eeg_df)))
    eeg_df = pd.concat([eeg_df] * repeats, ignore_index=True)
    eeg_df = eeg_df.iloc[:len(ecg_df)]

# Reset index
ecg_df = ecg_df.reset_index(drop=True)
eeg_df = eeg_df.reset_index(drop=True)

# ---------------------------
# Combine
# ---------------------------

fusion_df = pd.concat([ecg_df, eeg_df], axis=1)

# ---------------------------
# Create Stress Features
# ---------------------------

# Beta / Alpha ratio
fusion_df["Beta_Alpha_Ratio"] = fusion_df["Beta"] / (fusion_df["Alpha"] + 1e-10)

# Normalize components
fusion_df["HR_norm"] = fusion_df["Avg_Heart_Rate"] / fusion_df["Avg_Heart_Rate"].max()
fusion_df["LFHF_norm"] = fusion_df["LF_HF_Ratio"] / fusion_df["LF_HF_Ratio"].max()
fusion_df["BA_norm"] = fusion_df["Beta_Alpha_Ratio"] / fusion_df["Beta_Alpha_Ratio"].max()

# Final NeuroCardiac Stress Index
fusion_df["NeuroCardiac_Stress_Index"] = (
    0.4 * fusion_df["BA_norm"] +
    0.3 * fusion_df["LFHF_norm"] +
    0.3 * fusion_df["HR_norm"]
)

# ---------------------------
# Stress Category (Optional ML label)
# ---------------------------

fusion_df["Stress_Level"] = pd.cut(
    fusion_df["NeuroCardiac_Stress_Index"],
    bins=[0, 0.4, 0.7, 1.0],
    labels=["Low", "Medium", "High"]
)

# Save
fusion_df.to_csv("neurocardiac_features.csv", index=False)

print("\n✅ Fusion Complete Successfully")
print(fusion_df.head())