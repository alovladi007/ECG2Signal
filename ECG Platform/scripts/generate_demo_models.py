#!/usr/bin/env python3
"""
Generate demo model weights for ECG2Signal.

Creates tiny, lightweight model weights for demonstration purposes.
These are NOT trained models - just initialized weights for testing the pipeline.
"""
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path
import onnx
import onnxruntime as ort
import sys

sys.path.insert(0, '..')


def create_demo_unet():
    """Create a tiny U-Net model for demo purposes."""
    from ecg2signal.segment.models.unet import UNet
    
    print("Creating demo U-Net model...")
    model = UNet(
        in_channels=1,
        out_channels=3,  # grid, waveform, text
        features=[16, 32, 64],  # Very small for demo
        dropout=0.1
    )
    
    # Initialize with reasonable weights
    for m in model.modules():
        if isinstance(m, nn.Conv2d):
            nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
        elif isinstance(m, nn.BatchNorm2d):
            nn.init.constant_(m.weight, 1)
            nn.init.constant_(m.bias, 0)
    
    return model


def export_to_onnx(model, output_path, input_shape=(1, 1, 512, 512)):
    """Export PyTorch model to ONNX format."""
    print(f"Exporting to ONNX: {output_path}")
    
    # Create dummy input
    dummy_input = torch.randn(*input_shape)
    
    # Export
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size', 2: 'height', 3: 'width'},
            'output': {0: 'batch_size', 2: 'height', 3: 'width'}
        }
    )
    
    # Verify
    onnx_model = onnx.load(output_path)
    onnx.checker.check_model(onnx_model)
    print(f"✅ ONNX model exported and verified")
    
    # Test inference
    ort_session = ort.InferenceSession(output_path)
    input_name = ort_session.get_inputs()[0].name
    output = ort_session.run(None, {input_name: dummy_input.numpy()})
    print(f"✅ ONNX inference test passed, output shape: {output[0].shape}")


def create_demo_layout_cnn():
    """Create a tiny layout detection CNN."""
    print("Creating demo Layout CNN...")
    
    class TinyLayoutCNN(nn.Module):
        def __init__(self, num_classes=13):
            super().__init__()
            self.features = nn.Sequential(
                nn.Conv2d(1, 16, kernel_size=3, padding=1),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(2, 2),
                nn.Conv2d(16, 32, kernel_size=3, padding=1),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(2, 2),
                nn.AdaptiveAvgPool2d((8, 8))
            )
            self.classifier = nn.Sequential(
                nn.Flatten(),
                nn.Linear(32 * 8 * 8, 256),
                nn.ReLU(inplace=True),
                nn.Dropout(0.5),
                nn.Linear(256, num_classes * 5)  # 5 = (x, y, w, h, conf)
            )
        
        def forward(self, x):
            x = self.features(x)
            x = self.classifier(x)
            return x.view(-1, 13, 5)
    
    model = TinyLayoutCNN()
    
    # Initialize weights
    for m in model.modules():
        if isinstance(m, nn.Conv2d) or isinstance(m, nn.Linear):
            nn.init.kaiming_normal_(m.weight)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)
    
    return model


def create_demo_ocr():
    """Create a tiny OCR transformer."""
    print("Creating demo OCR model...")
    
    class TinyOCR(nn.Module):
        def __init__(self, vocab_size=100):
            super().__init__()
            self.cnn = nn.Sequential(
                nn.Conv2d(1, 16, kernel_size=3, padding=1),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(2, 2),
                nn.Conv2d(16, 32, kernel_size=3, padding=1),
                nn.ReLU(inplace=True),
                nn.AdaptiveAvgPool2d((4, 4))
            )
            self.fc = nn.Linear(32 * 4 * 4, vocab_size)
        
        def forward(self, x):
            x = self.cnn(x)
            x = x.view(x.size(0), -1)
            x = self.fc(x)
            return x
    
    model = TinyOCR()
    
    # Initialize weights
    for m in model.modules():
        if isinstance(m, nn.Conv2d) or isinstance(m, nn.Linear):
            nn.init.kaiming_normal_(m.weight)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)
    
    return model


def main():
    """Generate all demo models."""
    print("=" * 70)
    print("ECG2Signal Demo Model Generator")
    print("=" * 70)
    print("\nWARNING: These are NOT trained models!")
    print("These are randomly initialized weights for demonstration only.")
    print("For production use, train models with real ECG data.\n")
    
    # Create models directory
    models_dir = Path('models')
    models_dir.mkdir(exist_ok=True)
    print(f"Output directory: {models_dir.absolute()}\n")
    
    # 1. U-Net for segmentation
    print("\n1. U-Net Segmentation Model")
    print("-" * 70)
    unet = create_demo_unet()
    unet.eval()
    export_to_onnx(
        unet,
        models_dir / 'unet_weights.onnx',
        input_shape=(1, 1, 512, 512)
    )
    
    # Also save PyTorch checkpoint
    torch.save({
        'model_state_dict': unet.state_dict(),
        'config': {
            'in_channels': 1,
            'out_channels': 3,
            'features': [16, 32, 64]
        }
    }, models_dir / 'unet_demo.pth')
    print(f"✅ Saved PyTorch checkpoint: {models_dir}/unet_demo.pth")
    
    # 2. Layout CNN
    print("\n2. Layout Detection CNN")
    print("-" * 70)
    layout_cnn = create_demo_layout_cnn()
    layout_cnn.eval()
    export_to_onnx(
        layout_cnn,
        models_dir / 'layout_cnn.onnx',
        input_shape=(1, 1, 256, 256)
    )
    
    torch.save({
        'model_state_dict': layout_cnn.state_dict(),
        'config': {'num_classes': 13}
    }, models_dir / 'layout_demo.pth')
    print(f"✅ Saved PyTorch checkpoint: {models_dir}/layout_demo.pth")
    
    # 3. OCR Transformer
    print("\n3. OCR Model")
    print("-" * 70)
    ocr = create_demo_ocr()
    ocr.eval()
    export_to_onnx(
        ocr,
        models_dir / 'ocr_transformer.onnx',
        input_shape=(1, 1, 64, 256)
    )
    
    torch.save({
        'model_state_dict': ocr.state_dict(),
        'config': {'vocab_size': 100}
    }, models_dir / 'ocr_demo.pth')
    print(f"✅ Saved PyTorch checkpoint: {models_dir}/ocr_demo.pth")
    
    # Create README
    print("\n4. Creating README")
    print("-" * 70)
    readme_content = """# Demo Model Weights

⚠️ **WARNING: These are NOT trained models!**

These weights are randomly initialized for demonstration and testing purposes only.

## Files

- `unet_weights.onnx` (ONNX) - U-Net for image segmentation
- `unet_demo.pth` (PyTorch) - U-Net checkpoint
- `layout_cnn.onnx` (ONNX) - Layout detection CNN
- `layout_demo.pth` (PyTorch) - Layout CNN checkpoint
- `ocr_transformer.onnx` (ONNX) - OCR model
- `ocr_demo.pth` (PyTorch) - OCR checkpoint

## Usage

These models can be used to test the ECG2Signal pipeline without requiring
trained weights. However, they will NOT produce accurate results.

### For Production Use

Train models with real ECG data:

```bash
# Train U-Net
python -m ecg2signal.training.train_unet

# Train layout detector
python -m ecg2signal.training.train_layout

# Train OCR
python -m ecg2signal.training.train_ocr
```

### Model Sizes

- U-Net: Very small (features=[16, 32, 64])
- Layout CNN: Tiny architecture
- OCR: Minimal transformer

These small sizes are intentional for fast demos and testing.

## Training Your Own Models

1. Collect ECG image dataset (or use PhysioNet)
2. Generate synthetic training data with `synth_ecg.py`
3. Configure training in `training/configs/`
4. Run training scripts
5. Replace these demo weights with trained models

## Pre-trained Models

For production-quality models, consider:
- Training on PhysioNet datasets (PTB-XL, MIT-BIH)
- Using transfer learning from medical imaging models
- Fine-tuning on your specific ECG formats

## License

Demo weights: Public domain (not useful for actual ECG analysis)
"""
    
    with open(models_dir / 'README.md', 'w') as f:
        f.write(readme_content)
    print(f"✅ Created: {models_dir}/README.md")
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"\nGenerated {len(list(models_dir.glob('*')))} files in {models_dir}/")
    print("\nFiles:")
    for f in sorted(models_dir.glob('*')):
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  - {f.name:30s} ({size_mb:.2f} MB)")
    
    print("\n✅ Demo models generated successfully!")
    print("\nRemember: These are for DEMO/TESTING only.")
    print("Train with real data for production use!")
    print("=" * 70)


if __name__ == "__main__":
    main()
