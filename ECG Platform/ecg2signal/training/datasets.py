
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
