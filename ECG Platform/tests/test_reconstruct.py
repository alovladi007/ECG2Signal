
import numpy as np
from ecg2signal.reconstruct.postprocess import remove_baseline_wander, bandpass_filter

def test_baseline_removal():
    signal = np.sin(np.linspace(0, 10, 1000)) + 0.5 * np.linspace(0, 1, 1000)
    filtered = remove_baseline_wander(signal, 500)
    assert np.abs(np.mean(filtered)) < 0.1  # Baseline should be near zero

def test_bandpass_filter():
    signal = np.random.randn(1000)
    filtered = bandpass_filter(signal, 500)
    assert len(filtered) == len(signal)
