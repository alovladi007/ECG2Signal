
import numpy as np
from ecg2signal.types import LeadLayout

def trace_curves(waveform_image: np.ndarray, layout: LeadLayout) -> dict[str, np.ndarray]:
    curves = {}
    for lead in layout.leads:
        box = lead.box
        region = waveform_image[box.y:box.y2, box.x:box.x2]
        curve = extract_curve_from_region(region)
        curves[lead.name.value] = curve
    return curves

def extract_curve_from_region(region: np.ndarray) -> np.ndarray:
    if len(region.shape) == 3:
        import cv2
        gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
    else:
        gray = region
    h, w = gray.shape
    curve = np.zeros(w, dtype=np.float32)
    for x in range(w):
        col = gray[:, x]
        dark_pixels = np.where(col < 128)[0]
        if len(dark_pixels) > 0:
            curve[x] = float(np.mean(dark_pixels))
        else:
            curve[x] = h / 2.0
    return curve
