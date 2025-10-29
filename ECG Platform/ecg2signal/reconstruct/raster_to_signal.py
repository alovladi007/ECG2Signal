
import numpy as np
from ecg2signal.types import PaperSettings, LeadLayout
from ecg2signal.preprocess.scale_calibrate import pixels_to_voltage

def raster_to_signal(curves: dict[str, np.ndarray], paper_settings: PaperSettings, 
                    layout: LeadLayout) -> dict[str, np.ndarray]:
    signals = {}
    for lead_name, curve in curves.items():
        baseline = np.median(curve)
        signal = (baseline - curve) * (1.0 / paper_settings.pixels_per_mm) / paper_settings.gain
        signals[lead_name] = signal
    return signals
