# ECG2Signal - Setup & Integration Guide

This guide explains how to set up and use the newly integrated ECG2Signal package.

## Package Structure

The project has been reorganized into a proper Python package structure:

```
ECG Platform/
├── ecg2signal/              # Main package
│   ├── __init__.py          # Main ECGConverter class
│   ├── config.py            # Configuration management
│   ├── types.py             # Type definitions
│   ├── logging_conf.py      # Logging setup
│   │
│   ├── io/                  # I/O operations
│   │   ├── image_io.py      # Image loading/saving
│   │   ├── pdf.py           # PDF extraction
│   │   ├── wfdb_io.py       # WFDB format export
│   │   ├── edf_io.py        # EDF+ format export
│   │   ├── fhir.py          # HL7 FHIR export
│   │   └── dcm_waveform.py  # DICOM waveform export
│   │
│   ├── preprocess/          # Image preprocessing
│   │   ├── detect_page.py   # Page region detection
│   │   ├── denoise.py       # Image denoising
│   │   ├── dewarp.py        # Perspective correction
│   │   ├── grid_detect.py   # Grid line detection
│   │   └── scale_calibrate.py  # Calibration
│   │
│   ├── layout/              # Layout analysis
│   │   ├── lead_layout.py   # Lead detection
│   │   └── ocr_labels.py    # Text extraction
│   │
│   ├── segment/             # Image segmentation
│   │   ├── models/
│   │   │   └── unet.py      # U-Net segmentation model
│   │   ├── separate_layers.py  # Layer separation
│   │   └── trace_curve.py   # Curve tracing
│   │
│   ├── reconstruct/         # Signal reconstruction
│   │   ├── raster_to_signal.py  # Pixel to signal
│   │   ├── resample.py      # Resampling
│   │   ├── align_leads.py   # Lead alignment
│   │   └── postprocess.py   # Signal filtering
│   │
│   ├── clinical/            # Clinical analysis
│   │   ├── intervals.py     # Interval detection
│   │   ├── quality.py       # Quality metrics
│   │   └── reports.py       # Report generation
│   │
│   ├── training/            # ML model training
│   │   ├── synth_ecg.py     # Synthetic ECG generation
│   │   ├── render.py        # ECG rendering
│   │   ├── datasets.py      # Dataset loaders
│   │   ├── augment.py       # Data augmentation
│   │   ├── metrics.py       # Training metrics
│   │   ├── train_unet.py    # U-Net training
│   │   └── export_onnx.py   # Model export
│   │
│   ├── api/                 # REST API
│   │   └── main.py          # FastAPI application
│   │
│   ├── cli/                 # Command-line interface
│   │   └── ecg2signal.py    # CLI implementation
│   │
│   ├── ui/                  # Web interface
│   │   └── app.py           # Streamlit app
│   │
│   └── utils/               # Utility functions
│       ├── viz.py           # Visualization
│       ├── timeit.py        # Performance timing
│       └── tempfile_utils.py  # Temp file handling
│
├── tests/                   # Test suite
│   ├── test_integration.py  # Integration tests
│   ├── test_*.py            # Unit tests
│   └── conftest.py          # Pytest configuration
│
├── docs/                    # Documentation
│   └── *.md                 # Various docs
│
├── configs/                 # Model configurations
│   ├── unet_small.yaml
│   ├── layout_cnn.yaml
│   └── ocr_tiny.yaml
│
├── scripts/                 # Utility scripts
│   ├── download_demo_models.sh
│   └── benchmark.sh
│
├── run_api.py              # API server entry point
├── run_ui.py               # UI entry point
├── pyproject.toml          # Package configuration
├── requirements.txt        # Dependencies
└── README.md               # Main documentation
```

## Installation

### 1. Install the package

From the `ECG Platform` directory:

```bash
# Development installation (editable)
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"

# Or with all dependencies
pip install -e ".[all]"
```

### 2. Install from requirements.txt (alternative)

```bash
pip install -r requirements.txt
pip install -e .
```

### 3. Verify installation

```bash
# Check that CLI is available
ecg2signal --help

# Run integration tests
pytest tests/test_integration.py -v
```

## Usage

### 1. Command-Line Interface (CLI)

```bash
# Convert a single ECG image
ecg2signal convert input.jpg --output ./output --format wfdb

# With custom parameters
ecg2signal convert input.pdf --speed 50 --gain 5 --format edf

# Batch processing
ecg2signal batch ./input_folder/ --output ./output --workers 4
```

### 2. Python API

```python
from ecg2signal import ECGConverter

# Initialize converter
converter = ECGConverter()

# Convert an image
result = converter.convert(
    "ecg_image.jpg",
    paper_speed=25.0,
    gain=10.0,
    sample_rate=500
)

# Access signals
for lead in result.signals:
    print(f"{lead.name}: {len(lead.signal)} samples")

# Export to different formats
result.export_wfdb("output/")
result.export_edf("output/ecg.edf")
result.export_json("output/ecg.json")

# Check quality metrics
print(f"Quality score: {result.quality_metrics.overall_score}")
print(f"SNR: {result.quality_metrics.snr}")
```

### 3. REST API

Start the API server:

```bash
# Using the run script
python run_api.py

# Or using uvicorn directly
uvicorn ecg2signal.api.main:app --reload --host 0.0.0.0 --port 8000
```

API endpoints:
- `GET /` - API info
- `GET /health` - Health check
- `POST /convert` - Convert ECG image

Example API call:
```bash
curl -X POST "http://localhost:8000/convert" \
  -F "file=@ecg_image.jpg" \
  -F "format=wfdb" \
  -F "paper_speed=25.0" \
  -F "gain=10.0"
```

### 4. Web UI (Streamlit)

Start the web interface:

```bash
# Using the run script
python run_ui.py

# Or using streamlit directly
streamlit run ecg2signal/ui/app.py
```

Then open http://localhost:8501 in your browser.

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Application
APP_NAME=ECG2Signal
ENV=production
DEBUG=false
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Model Paths
MODEL_DIR=./models
UNET_MODEL_PATH=./models/unet_weights.onnx
OCR_MODEL_PATH=./models/ocr_transformer.onnx
LAYOUT_MODEL_PATH=./models/layout_cnn.onnx

# Processing
DEFAULT_SAMPLE_RATE=500
DEFAULT_PAPER_SPEED=25.0
DEFAULT_GAIN=10.0
MAX_IMAGE_SIZE=4096

# Export
DEFAULT_EXPORT_FORMAT=wfdb
EXPORT_DIR=./outputs

# Performance
USE_GPU=true
GPU_DEVICE=0
PARALLEL_INFERENCE=true
```

### Python Configuration

```python
from ecg2signal.config import Settings

settings = Settings(
    log_level="DEBUG",
    default_paper_speed=50.0,
    default_gain=5.0,
    use_gpu=False,
)

converter = ECGConverter(settings)
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ecg2signal --cov-report=html

# Run specific test file
pytest tests/test_integration.py -v

# Run specific test
pytest tests/test_integration.py::TestIntegration::test_package_imports -v
```

### Code Quality

```bash
# Format code
black ecg2signal/
isort ecg2signal/

# Lint code
ruff ecg2signal/

# Type checking
mypy ecg2signal/
```

### Building the Package

```bash
# Build distribution
python -m build

# Install built package
pip install dist/ecg2signal-0.1.0-py3-none-any.whl
```

## Docker Deployment

### Build Image

```bash
docker build -t ecg2signal:latest .
```

### Run Container

```bash
# API server
docker run -p 8000:8000 ecg2signal:latest

# Or using docker-compose
docker-compose up
```

## Troubleshooting

### Import Errors

If you get import errors, ensure the package is installed:

```bash
pip install -e .
```

### Missing Dependencies

Install all dependencies:

```bash
pip install -r requirements.txt
```

### Model Not Found Errors

The current implementation uses stub ML models. For production use, you'll need to:

1. Train actual models using the training module
2. Download pre-trained models (when available)
3. Place model files in the `models/` directory

### GPU Issues

If you have GPU issues, disable GPU in settings:

```python
settings = Settings(use_gpu=False)
```

## Next Steps

1. **Train ML Models**: The current models are stubs. Train real models using:
   ```bash
   python -m ecg2signal.training.train_unet --config configs/unet_small.yaml
   ```

2. **Add Test Data**: Place sample ECG images in a `test_data/` directory

3. **Configure for Production**: Update `.env` file with production settings

4. **Deploy**: Use Docker or your preferred deployment method

## Support

For issues, questions, or contributions:
- Check existing documentation in `docs/`
- Run tests to verify setup
- Review code examples in `tests/`

## Integration Complete!

All modules are now properly integrated and organized. The package provides:

✅ Proper Python package structure
✅ Unified imports from `ecg2signal`
✅ Multiple interfaces (CLI, API, UI, Python)
✅ Comprehensive configuration system
✅ Complete testing framework
✅ Production-ready deployment options
