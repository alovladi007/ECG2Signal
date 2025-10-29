# ECG2Signal - Quick Start Guide

Get started with ECG2Signal in 5 minutes!

## Installation

```bash
cd "ECG Platform"
pip install -e .
```

## Basic Usage

### 1. Python API (Recommended)

```python
from ecg2signal import ECGConverter

# Create converter
converter = ECGConverter()

# Convert an ECG image
result = converter.convert(
    "path/to/ecg_image.jpg",
    paper_speed=25.0,  # mm/s
    gain=10.0,         # mm/mV
    sample_rate=500    # Hz
)

# Access results
print(f"Detected {len(result.signals)} leads")
print(f"Quality score: {result.quality_metrics.overall_score:.2f}")

# Export to different formats
result.export_wfdb("output/")        # PhysioNet WFDB
result.export_edf("output/ecg.edf")  # EDF+
result.export_json("output/ecg.json") # JSON
```

### 2. Command Line

```bash
# Simple conversion
ecg2signal convert ecg_image.jpg --output ./output

# With parameters
ecg2signal convert ecg_image.pdf \
  --output ./output \
  --format wfdb \
  --speed 25.0 \
  --gain 10.0

# Batch processing
ecg2signal batch ./input_folder/ --output ./output
```

### 3. REST API

Start the server:
```bash
python run_api.py
```

Use the API:
```bash
curl -X POST "http://localhost:8000/convert" \
  -F "file=@ecg_image.jpg" \
  -F "format=wfdb" \
  -F "paper_speed=25.0" \
  -F "gain=10.0"
```

### 4. Web Interface

```bash
python run_ui.py
# Opens at http://localhost:8501
```

## Common Tasks

### Convert a Single Image

```python
from ecg2signal import ECGConverter

converter = ECGConverter()
result = converter.convert("ecg.jpg")
result.export_wfdb("output/")
```

### Batch Process Multiple Files

```python
from ecg2signal import ECGConverter
from pathlib import Path

converter = ECGConverter()
image_files = list(Path("input/").glob("*.jpg"))
results = converter.convert_batch(
    [str(f) for f in image_files],
    output_dir="output/"
)
```

### Customize Settings

```python
from ecg2signal import ECGConverter, Settings

settings = Settings(
    log_level="DEBUG",
    default_paper_speed=50.0,
    default_gain=5.0,
    use_gpu=False
)

converter = ECGConverter(settings)
result = converter.convert("ecg.jpg")
```

### Access Signal Data

```python
result = converter.convert("ecg.jpg")

# Get all signals
for lead in result.signals:
    print(f"{lead.name}: {len(lead.signal)} samples")
    print(f"  Signal range: {lead.signal.min():.3f} to {lead.signal.max():.3f} mV")

# Access specific lead
lead_i = next(s for s in result.signals if s.name == "I")
print(f"Lead I: {lead_i.signal}")

# Get metadata
print(f"Paper speed: {result.paper_settings.paper_speed_mm_s} mm/s")
print(f"Gain: {result.paper_settings.gain_mm_mv} mm/mV")
print(f"Sample rate: {result.sample_rate} Hz")
```

### Quality Metrics

```python
result = converter.convert("ecg.jpg")

quality = result.quality_metrics
print(f"Overall score: {quality.overall_score:.2f}")
print(f"SNR: {quality.snr:.2f} dB")
print(f"Baseline drift: {quality.baseline_drift:.3f}")
print(f"Coverage: {quality.coverage:.2%}")
```

## Module Examples

### Image I/O

```python
from ecg2signal.io import load_image, save_image

# Load image
image = load_image("ecg.jpg")
print(f"Image shape: {image.shape}")

# Save processed image
save_image(image, "output.png", quality=95)
```

### Preprocessing

```python
from ecg2signal.io import load_image
from ecg2signal.preprocess import denoise_image, detect_grid, dewarp_image

image = load_image("ecg.jpg")
denoised = denoise_image(image, method="bilateral")
dewarped = dewarp_image(denoised)
grid_info = detect_grid(dewarped)
print(f"Grid detected: {grid_info is not None}")
```

### Layout Detection

```python
from ecg2signal.layout import LeadLayoutDetector
from ecg2signal.io import load_image

image = load_image("ecg.jpg")
detector = LeadLayoutDetector()
layout = detector.detect(image)

print(f"Layout type: {layout.layout_type}")
print(f"Number of leads: {len(layout.leads)}")
for lead in layout.leads:
    print(f"  {lead.name}: box={lead.box}")
```

### Export Formats

```python
# Export to all formats
result.export_wfdb("output/")              # PhysioNet WFDB
result.export_edf("output/ecg.edf")        # EDF+
result.export_json("output/ecg.json")      # JSON
result.export_csv("output/")               # CSV
result.export_fhir("output/fhir.json")     # HL7 FHIR
result.export_dicom("output/ecg.dcm")      # DICOM

# Or export all at once
result.export_all("output/")
```

## Testing

Run tests to verify installation:

```bash
# Run all tests
pytest

# Run integration tests
pytest tests/test_integration.py -v

# Run with coverage
pytest --cov=ecg2signal
```

## Configuration

Create a `.env` file for custom settings:

```bash
# .env file
LOG_LEVEL=DEBUG
DEFAULT_PAPER_SPEED=25.0
DEFAULT_GAIN=10.0
USE_GPU=true
MODEL_DIR=./models
```

## Troubleshooting

### Module Not Found

```bash
# Make sure package is installed
pip install -e .
```

### Model Errors

The current implementation uses stub ML models for testing. For production use, you'll need actual trained models.

### Import Errors

```python
# Make sure to import from ecg2signal package
from ecg2signal import ECGConverter  # ✓ Correct
from ECGConverter import ...          # ✗ Wrong
```

## Next Steps

1. **Read SETUP.md** for detailed installation and configuration
2. **Check INTEGRATION_SUMMARY.md** for complete architecture overview
3. **Explore docs/** for detailed documentation on each module
4. **Run examples** above to familiarize yourself with the API

## Package Structure

All modules are organized under `ecg2signal`:

```python
# Main API
from ecg2signal import ECGConverter, Settings

# I/O
from ecg2signal.io import load_image, export_wfdb, export_edf

# Preprocessing
from ecg2signal.preprocess import denoise_image, detect_grid

# Layout
from ecg2signal.layout import LeadLayoutDetector, OCREngine

# Segmentation
from ecg2signal.segment import separate_layers, trace_curves

# Reconstruction
from ecg2signal.reconstruct import raster_to_signal, resample_signals

# Clinical
from ecg2signal.clinical import compute_intervals, compute_quality_metrics

# Utilities
from ecg2signal.utils import plot_ecg, timeit
```

## Support

For detailed information:
- **Installation**: See SETUP.md
- **Architecture**: See INTEGRATION_SUMMARY.md
- **API Reference**: See docs/api.md
- **Examples**: See tests/test_integration.py

Happy converting! 🫀📈
