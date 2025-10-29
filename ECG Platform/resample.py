
import numpy as np
from scipy.signal import resample

def resample_signals(signals: dict[str, np.ndarray], paper_settings, target_sr: int) -> dict[str, np.ndarray]:
    resampled = {}
    for lead_name, signal in signals.items():
        original_length = len(signal)
        duration_sec = original_length / paper_settings.pixels_per_second
        target_length = int(duration_sec * target_sr)
        resampled[lead_name] = resample(signal, target_length)
    return resampled
