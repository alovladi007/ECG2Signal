"""Segmentation module for separating grid, waveform, and text layers."""

from ecg2signal.segment.separate_layers import separate_layers
from ecg2signal.segment.trace_curve import trace_curves

__all__ = [
    "separate_layers",
    "trace_curves",
]
