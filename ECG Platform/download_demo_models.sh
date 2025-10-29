#!/bin/bash
echo "Downloading demo models..."
mkdir -p models
echo "Demo models would be downloaded here"
touch models/unet_weights.onnx
touch models/ocr_transformer.onnx
touch models/layout_cnn.onnx
echo "✓ Demo models ready"
