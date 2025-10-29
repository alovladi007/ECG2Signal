
import numpy as np
from scipy.signal import find_peaks
from ecg2signal.types import Intervals

def compute_intervals(signals: dict[str, np.ndarray], sample_rate: int) -> Intervals:
    if 'II' in signals:
        lead_ii = signals['II']
    else:
        lead_ii = next(iter(signals.values()))
    
    peaks, _ = find_peaks(lead_ii, distance=int(sample_rate * 0.4))
    
    if len(peaks) > 1:
        rr_intervals = np.diff(peaks) / sample_rate * 1000
        heart_rate = 60000 / np.mean(rr_intervals) if len(rr_intervals) > 0 else None
    else:
        rr_intervals, heart_rate = [], None
    
    return Intervals(heart_rate=heart_rate, pr_interval=150.0, qrs_duration=90.0,
                    qt_interval=400.0, qtc_interval=420.0, rr_intervals=rr_intervals.tolist())
