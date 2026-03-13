import wfdb
import matplotlib.pyplot as plt

# Read ECG record (100)
record = wfdb.rdrecord("100")
signal = record.p_signal
fs = record.fs

print("Sampling Frequency:", fs)
print("Signal Shape:", signal.shape)

# Plot first 1000 samples
plt.plot(signal[:1000])
plt.title("ECG Signal - Record 100")
plt.xlabel("Samples")
plt.ylabel("Amplitude")
plt.show()