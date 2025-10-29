
"""Data augmentation for ECG images."""
import albumentations as A

def get_training_augmentation():
    return A.Compose([
        A.Rotate(limit=15, p=0.5),
        A.RandomBrightnessContrast(p=0.3),
        A.GaussianBlur(p=0.2),
        A.GridDistortion(p=0.2),
        A.OpticalDistortion(p=0.2),
    ])

def get_validation_augmentation():
    return A.Compose([])
