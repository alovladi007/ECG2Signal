
"""Training metrics."""
import numpy as np

def compute_iou(pred, target):
    intersection = np.logical_and(pred, target).sum()
    union = np.logical_or(pred, target).sum()
    return intersection / (union + 1e-6)

def compute_dice(pred, target):
    intersection = (pred * target).sum()
    return 2 * intersection / (pred.sum() + target.sum() + 1e-6)
