
"""Synthetic ECG data generation."""
import numpy as np

def generate_synthetic_ecg(duration: float = 10.0, fs: int = 500) -> np.ndarray:
    """Generate synthetic ECG signal."""
    t = np.arange(0, duration, 1/fs)
    hr = 75  # BPM
    rr_interval = 60.0 / hr
    
    ecg = np.zeros_like(t)
    beat_times = np.arange(0, duration, rr_interval)
    
    for beat_t in beat_times:
        idx = int(beat_t * fs)
        if idx < len(ecg):
            ecg[idx:idx+50] += np.sin(np.linspace(0, np.pi, 50)) * 0.5
    
    return ecg
