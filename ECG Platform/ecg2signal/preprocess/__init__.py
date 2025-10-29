"""Preprocessing module for ECG image enhancement and calibration."""

from ecg2signal.preprocess.detect_page import detect_page_region
from ecg2signal.preprocess.denoise import denoise_image
from ecg2signal.preprocess.dewarp import dewarp_image
from ecg2signal.preprocess.grid_detect import detect_grid
from ecg2signal.preprocess.scale_calibrate import calibrate_scale

__all__ = [
    "detect_page_region",
    "denoise_image",
    "dewarp_image",
    "detect_grid",
    "calibrate_scale",
]
