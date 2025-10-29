#!/usr/bin/env python3
from pathlib import Path

configs = {

"ecg2signal/training/configs/unet_small.yaml": '''
model:
  name: unet_small
  in_channels: 3
  out_channels: 3
  features: [32, 64, 128, 256]

training:
  epochs: 100
  batch_size: 16
  learning_rate: 0.001
  optimizer: adam
  scheduler: cosine

data:
  train_split: 0.8
  val_split: 0.1
  test_split: 0.1
  augmentation: true
  
augmentation:
  rotation: 15
  scale: 0.1
  brightness: 0.2
  contrast: 0.2
''',

"ecg2signal/training/configs/layout_cnn.yaml": '''
model:
  name: layout_cnn
  backbone: resnet18
  num_classes: 13  # 12 leads + rhythm

training:
  epochs: 50
  batch_size: 32
  learning_rate: 0.0001

data:
  image_size: [512, 768]
''',

"ecg2signal/training/configs/ocr_tiny.yaml": '''
model:
  name: transformer_ocr
  d_model: 256
  nhead: 8
  num_layers: 4

training:
  epochs: 200
  batch_size: 64
  learning_rate: 0.0005
''',

}

for path, content in configs.items():
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content)
    print(f"Created {path}")

# Add more training modules
training_modules = {

"ecg2signal/training/datasets.py": '''
"""Dataset loaders for training."""
from torch.utils.data import Dataset
import numpy as np

class ECGDataset(Dataset):
    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        
    def __len__(self):
        return 1000  # Placeholder
        
    def __getitem__(self, idx):
        # Load and return data
        image = np.random.rand(3, 512, 512)
        mask = np.random.randint(0, 3, (512, 512))
        return image, mask
''',

"ecg2signal/training/augment.py": '''
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
''',

"ecg2signal/training/metrics.py": '''
"""Training metrics."""
import numpy as np

def compute_iou(pred, target):
    intersection = np.logical_and(pred, target).sum()
    union = np.logical_or(pred, target).sum()
    return intersection / (union + 1e-6)

def compute_dice(pred, target):
    intersection = (pred * target).sum()
    return 2 * intersection / (pred.sum() + target.sum() + 1e-6)
''',

"ecg2signal/training/data_synth/render.py": '''
"""Render synthetic ECG images."""
import numpy as np
import matplotlib.pyplot as plt

def render_ecg_to_image(signal, paper_speed=25.0, gain=10.0, dpi=300):
    """Render ECG signal to image with grid."""
    duration = len(signal) / 500  # Assume 500 Hz
    
    fig, ax = plt.subplots(figsize=(10, 4), dpi=dpi)
    time = np.arange(len(signal)) / 500
    ax.plot(time, signal, 'k-', linewidth=0.5)
    ax.grid(True, which='both', linestyle='-', linewidth=0.3, alpha=0.5)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude (mV)')
    
    # Convert to image
    fig.canvas.draw()
    img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    plt.close(fig)
    
    return img
''',

}

for path, content in training_modules.items():
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content)
    print(f"Created {path}")

print(f"\n✓ Training configuration complete")

