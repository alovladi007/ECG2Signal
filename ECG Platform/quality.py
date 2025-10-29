
import numpy as np
from ecg2signal.types import QualityMetrics

def compute_quality_metrics(signals: dict[str, np.ndarray], sample_rate: int) -> QualityMetrics:
    snr_values, drift_values, clip_values = [], [], []
    
    for name, signal in signals.items():
        snr = estimate_snr(signal)
        drift = estimate_baseline_drift(signal)
        clipping = estimate_clipping_ratio(signal)
        snr_values.append(snr)
        drift_values.append(drift)
        clip_values.append(clipping)
    
    return QualityMetrics(
        snr=float(np.mean(snr_values)),
        baseline_drift=float(np.mean(drift_values)),
        clipping_ratio=float(np.mean(clip_values)),
        coverage=0.95,
        confidence=0.85,
        lead_quality={name: 0.8 for name in signals.keys()}
    )

def estimate_snr(signal: np.ndarray) -> float:
    signal_power = np.var(signal)
    noise_power = np.var(np.diff(signal)) / 2
    return 10 * np.log10(signal_power / (noise_power + 1e-10))

def estimate_baseline_drift(signal: np.ndarray) -> float:
    from scipy.signal import detrend
    detrended = detrend(signal)
    drift = np.std(signal - detrended) / (np.std(signal) + 1e-10)
    return float(drift)

def estimate_clipping_ratio(signal: np.ndarray) -> float:
    threshold = 0.99
    max_val, min_val = np.max(signal), np.min(signal)
    signal_range = max_val - min_val
    clipped = np.sum((signal > max_val - signal_range * 0.01) | (signal < min_val + signal_range * 0.01))
    return float(clipped / len(signal))
