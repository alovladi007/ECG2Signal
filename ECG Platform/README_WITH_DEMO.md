# ECG2Signal - Complete with Working Demo

**Production-grade ECG image to digital signal conversion**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Convert ECG images (scans, photos, PDFs) into calibrated digital time-series signals with support for multiple clinical formats.

---

## 🎉 Now with Complete Working Demo!

This package includes **everything you need** to start using ECG2Signal immediately:

- ✅ **Professional Python package** with 52 modules
- ✅ **Interactive Jupyter notebook** tutorial
- ✅ **Automated setup** script
- ✅ **Demo ML models** (ready to use)
- ✅ **Multiple interfaces** (CLI, API, Web UI)
- ✅ **Comprehensive documentation**

**[👉 Start with the Demo →](START_HERE.md)**

---

## Quick Start

### 1. Install

```bash
pip install -e .
```

### 2. Run Demo Setup

```bash
python setup_demo.py
```

### 3. Try the Demo

```bash
# Interactive notebook (recommended!)
jupyter notebook notebooks/complete_demo.ipynb

# Or try the CLI
ecg2signal convert sample.jpg --output ./output

# Or start the API
python run_api.py

# Or launch the Web UI
python run_ui.py
```

---

## Features

### Input Formats
- **Images**: JPG, PNG, TIFF
- **Documents**: PDF (single/multi-page)
- **Sources**: Scans, mobile photos, screenshots

### Processing Capabilities
- Automatic grid detection and calibration
- Perspective correction and dewarping
- Multi-lead layout detection (12-lead support)
- ML-based segmentation (U-Net)
- Signal reconstruction with clinical calibration
- Quality metrics and validation

### Export Formats
- **WFDB** - PhysioNet format
- **EDF+** - European Data Format
- **HL7 FHIR** - Healthcare interoperability standard
- **DICOM** - Waveform format
- **JSON** - Structured data
- **CSV** - Spreadsheet format

### Clinical Features
- PR, QRS, QT interval detection
- Heart rate calculation
- Quality assessment (SNR, baseline drift)
- Multi-lead synchronization
- Rhythm strip analysis

---

## Usage Examples

### Python API

```python
from ecg2signal import ECGConverter

# Create converter
converter = ECGConverter()

# Convert ECG image
result = converter.convert("ecg_image.jpg")

# Access signals
for lead in result.signals:
    print(f"{lead.name}: {len(lead.signal)} samples")

# Export to different formats
result.export_wfdb("output/")
result.export_edf("output/ecg.edf")
result.export_json("output/ecg.json")

# Check quality
print(f"Quality: {result.quality_metrics.overall_score:.2f}")
```

### Command Line

```bash
# Single file
ecg2signal convert ecg.jpg --output ./output --format wfdb

# With parameters
ecg2signal convert ecg.pdf --speed 25 --gain 10 --format edf

# Batch processing
ecg2signal batch ./input_folder/ --output ./output
```

### REST API

```python
# Start server
python run_api.py
```

```bash
# Use API
curl -X POST "http://localhost:8000/convert" \
  -F "file=@ecg_image.jpg" \
  -F "format=wfdb"
```

### Web UI

```bash
python run_ui.py
# Opens at http://localhost:8501
```

---

## Package Structure

```
ecg2signal/
├── io/              # I/O operations (WFDB, EDF, DICOM, FHIR)
├── preprocess/      # Image preprocessing
├── layout/          # Layout detection
├── segment/         # ML segmentation
├── reconstruct/     # Signal reconstruction
├── clinical/        # Clinical analysis
├── training/        # ML model training
├── api/             # REST API
├── cli/             # Command-line interface
├── ui/              # Web interface
└── utils/           # Utilities

notebooks/           # Interactive tutorials
scripts/             # Utility scripts
tests/               # Test suite
docs/                # Documentation
```

---

## Demo Files

### New in Demo Package

1. **notebooks/complete_demo.ipynb** - Interactive 10-step tutorial
2. **scripts/generate_demo_models.py** - Demo ML model generator
3. **setup_demo.py** - Automated setup script
4. **test_installation.py** - Installation verification
5. **.env.example** - Configuration template

See [DEMO_INTEGRATION.md](DEMO_INTEGRATION.md) for complete details.

---

## Documentation

### Getting Started
- **[START_HERE.md](START_HERE.md)** - Begin here for demo
- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference guide
- **[SETUP.md](SETUP.md)** - Detailed setup instructions

### Architecture & Integration
- **[INTEGRATION_COMPLETE.md](INTEGRATION_COMPLETE.md)** - Integration summary
- **[INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)** - Technical details
- **[DEMO_INTEGRATION.md](DEMO_INTEGRATION.md)** - Demo additions

### Reference
- **[docs/](docs/)** - Module documentation
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Project overview

---

## Requirements

- Python >=3.11
- PyTorch >=2.0.0
- OpenCV >=4.8.0
- FastAPI >=0.103.0
- See [requirements.txt](requirements.txt) for complete list

---

## Installation Options

### Basic Installation

```bash
pip install -e .
```

### With Development Tools

```bash
pip install -e ".[dev]"
```

### With Training Tools

```bash
pip install -e ".[training]"
```

### Everything

```bash
pip install -e ".[all]"
```

---

## Testing

```bash
# Quick installation test
python test_installation.py

# Full test suite
pytest tests/

# With coverage
pytest --cov=ecg2signal

# Integration tests only
pytest tests/test_integration.py -v
```

---

## Configuration

### Using Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit settings
nano .env
```

### Using Python

```python
from ecg2signal import Settings

settings = Settings(
    log_level="DEBUG",
    default_paper_speed=50.0,
    use_gpu=False
)

converter = ECGConverter(settings)
```

---

## Development

### Project Structure

- **ecg2signal/** - Main Python package
- **tests/** - Test suite
- **notebooks/** - Jupyter notebooks
- **scripts/** - Utility scripts
- **docs/** - Documentation
- **configs/** - Model configurations

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black ecg2signal/
isort ecg2signal/

# Lint
ruff ecg2signal/

# Type check
mypy ecg2signal/
```

---

## Deployment

### Docker

```bash
# Build image
docker build -t ecg2signal:latest .

# Run container
docker run -p 8000:8000 ecg2signal:latest

# Or use docker-compose
docker-compose up
```

### Production Setup

1. Install dependencies
2. Generate/download production models
3. Configure environment variables
4. Set up monitoring and logging
5. Deploy using your preferred method

---

## Important Notes

### Demo Models

The models generated by `generate_demo_models.py` are **for demonstration only**:
- ✅ Fast and lightweight
- ✅ Functional for testing
- ❌ **NOT for clinical use**
- ❌ **NOT trained on real data**
- ❌ **NOT validated**

For production, you must train models on real ECG data and validate them properly.

### Clinical Use

This software is provided for **research and development purposes**. For clinical use:
- Validate all outputs
- Follow regulatory requirements
- Ensure proper training data
- Implement quality controls
- Maintain audit trails

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

Apache License 2.0 - See [LICENSE](LICENSE) for details.

---

## Citation

If you use this software in your research, please cite:

```bibtex
@software{ecg2signal,
  title = {ECG2Signal: Production-grade ECG Image to Signal Conversion},
  author = {ECG2Signal Contributors},
  year = {2025},
  url = {https://github.com/alovladi007/ECG2Signal}
}
```

---

## Support

- **Documentation**: See [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/alovladi007/ECG2Signal/issues)
- **Discussions**: [GitHub Discussions](https://github.com/alovladi007/ECG2Signal/discussions)

---

## Acknowledgments

Built with:
- PyTorch for ML framework
- OpenCV for image processing
- FastAPI for REST API
- Streamlit for web UI
- WFDB, MNE, pyEDFlib for clinical formats

---

## What's Next?

1. **[Start with the demo →](START_HERE.md)**
2. **[Read the quick start →](QUICKSTART.md)**
3. **[Explore the architecture →](INTEGRATION_SUMMARY.md)**
4. **[Try the interactive notebook →](notebooks/complete_demo.ipynb)**

---

**Ready to convert ECG images to signals? Get started now! 🚀**
