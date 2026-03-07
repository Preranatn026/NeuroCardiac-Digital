import pandas as pd
from sklearn.ensemble import IsolationForest

df = pd.read_csv("neurocardiac_features.csv")

features = [
    "Avg_Heart_Rate",
    "SDNN",
    "RMSSD",
    "LF_HF_Ratio",
    "Beta_Alpha_Ratio"
]

model = IsolationForest(contamination=0.2, random_state=42)
df["Anomaly"] = model.fit_predict(df[features])

df["Anomaly"] = df["Anomaly"].map({1: "Normal", -1: "Anomaly"})

df.to_csv("neurocardiac_with_anomaly.csv", index=False)

print("✅ Anomaly detection complete")
print(df[["Record", "Anomaly"]])