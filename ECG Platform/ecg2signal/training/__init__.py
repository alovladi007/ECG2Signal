"""Training module for ML models and synthetic data generation."""

from ecg2signal.training.synth_ecg import generate_synthetic_ecg
from ecg2signal.training.render import render_ecg_to_image
from ecg2signal.training.datasets import ECGDataset
from ecg2signal.training.augment import augment_ecg_image
from ecg2signal.training.metrics import compute_iou, compute_dice
from ecg2signal.training.train_unet import train_unet
from ecg2signal.training.export_onnx import export_to_onnx

__all__ = [
    "generate_synthetic_ecg",
    "render_ecg_to_image",
    "ECGDataset",
    "augment_ecg_image",
    "compute_iou",
    "compute_dice",
    "train_unet",
    "export_to_onnx",
]
