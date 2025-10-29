
import numpy as np
from scipy.signal import butter, filtfilt

def postprocess_signals(signals: dict[str, np.ndarray], sample_rate: int) -> dict[str, np.ndarray]:
    processed = {}
    for name, signal in signals.items():
        signal = remove_baseline_wander(signal, sample_rate)
        signal = bandpass_filter(signal, sample_rate)
        processed[name] = signal
    return processed

def remove_baseline_wander(signal: np.ndarray, fs: int) -> np.ndarray:
    b, a = butter(1, 0.5 / (fs / 2), btype='high')
    return filtfilt(b, a, signal)

def bandpass_filter(signal: np.ndarray, fs: int, lowcut: float = 0.5, highcut: float = 50.0) -> np.ndarray:
    nyq = fs / 2
    low, high = lowcut / nyq, highcut / nyq
    b, a = butter(2, [low, high], btype='band')
    return filtfilt(b, a, signal)
