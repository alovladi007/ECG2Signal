# ECG2Signal Quick Start Guide

Get started with ECG2Signal in 5 minutes! 🚀

## Prerequisites

- Python 3.11+
- pip package manager
- (Optional) CUDA-capable GPU for faster processing

## Installation

### Option 1: Quick Install (Recommended)

```bash
# Clone or extract the project
cd ecg2signal

# Install dependencies
pip install -r requirements.txt

# Generate demo models
python scripts/generate_demo_models.py
```

### Option 2: Development Install

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install
```

### Option 3: Docker

```bash
# Build and run
docker compose -f docker/compose.yaml up

# Access API at http://localhost:8000/docs
```

## Running Your First Conversion

### Method 1: Python API (Easiest)

```python
from ecg2signal import ECGConverter

# Initialize converter
converter = ECGConverter()

# Convert ECG image to signals
result = converter.convert(
    'path/to/ecg_image.jpg',
    paper_speed=25.0,  # mm/s
    gain=10.0          # mm/mV
)

# Access signals
for lead_name, signal in result.signals.items():
    print(f"{lead_name}: {len(signal)} samples")

# Get clinical measurements
print(f"Heart Rate: {result.intervals.heart_rate} BPM")
print(f"QRS Duration: {result.intervals.qrs_duration} ms")

# Export to different formats
result.export_wfdb('output/ecg')     # WFDB format
result.export_csv('output/ecg.csv')   # CSV
result.export_json('output/ecg.json') # JSON
```

### Method 2: Command Line

```bash
# Convert single file
python -m ecg2signal.cli.ecg2signal convert \
    input.jpg \
    --output output/ \
    --format wfdb \
    --paper-speed 25 \
    --gain 10

# Convert with options
python -m ecg2signal.cli.ecg2signal convert \
    scan.pdf \
    --output results/ \
    --format csv \
    --extract-intervals \
    --quality-check

# Batch conversion
python -m ecg2signal.cli.ecg2signal batch \
    ecg_images/*.jpg \
    --output batch_output/
```

### Method 3: Web API

Start the API server:

```bash
# Development mode
uvicorn ecg2signal.api.main:app --reload

# Production mode
uvicorn ecg2signal.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Access the interactive docs at: http://localhost:8000/docs

Example API request:

```python
import requests

# Upload and convert
with open('ecg.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/convert/',
        files={'file': f},
        data={
            'paper_speed': 25.0,
            'gain': 10.0,
            'export_format': 'wfdb'
        }
    )

result = response.json()
print(result['status'])
print(result['calibration'])
```

### Method 4: Web UI (Streamlit)

```bash
# Launch web interface
streamlit run ecg2signal/ui/app.py

# Opens browser at http://localhost:8501
```

Features:
- Drag-and-drop file upload
- Real-time processing
- Interactive signal visualization
- Export to multiple formats
- Quality metrics display

## Working with the Demo Notebook

The easiest way to learn ECG2Signal is through the interactive Jupyter notebook:

```bash
# Install Jupyter
pip install jupyter

# Launch notebook
cd notebooks
jupyter notebook complete_demo.ipynb
```

The notebook walks through:
1. Creating synthetic ECG images
2. Full preprocessing pipeline
3. Grid detection and calibration
4. Layout detection
5. Signal extraction
6. Clinical feature extraction
7. Quality assessment
8. Export to multiple formats

## Testing the Installation

### Quick Test

```bash
# Run validation script
python validate_project.py

# Should output:
# ✅ 79/79 required files present
# ✅ All required directories present
# ✅ Project structure complete!
```

### Run Test Suite

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=ecg2signal --cov-report=html

# Run specific test
pytest tests/test_api.py -v
```

### Test with Sample Data

```bash
# Test with included sample
python -m ecg2signal.cli.ecg2signal convert \
    tests/data/sample_ecg_photo.jpg \
    --output test_output/
```

## Common Workflows

### Workflow 1: Hospital ECG Scan Processing

```python
from ecg2signal import ECGConverter
from pathlib import Path

converter = ECGConverter()

# Process scanned ECG from hospital
result = converter.convert(
    'hospital_scan.pdf',
    paper_speed=25.0,
    gain=10.0
)

# Check quality
if result.quality_metrics.overall_quality > 0.8:
    # Export to EHR-compatible format
    result.export_fhir('output/ecg_fhir.json')
    result.export_dicom('output/ecg.dcm')
else:
    print("Warning: Low quality signal detected")
```

### Workflow 2: Mobile Photo Processing

```python
# Handle photos with perspective distortion
result = converter.convert(
    'mobile_photo.jpg',
    paper_speed=25.0,  # Usually standard
    gain=10.0
)

# Automatic dewarp and correction applied
# Extract for telemedicine
signals_dict = {name: list(sig) for name, sig in result.signals.items()}
```

### Workflow 3: Batch Hospital Archive

```python
from glob import glob

# Process entire archive
ecg_files = glob('archive/**/*.pdf', recursive=True)

results = converter.convert_batch(
    ecg_files,
    output_dir='processed/',
    paper_speed=25.0,
    gain=10.0
)

# Generate summary report
successful = sum(1 for r in results if r is not None)
print(f"Processed {successful}/{len(ecg_files)} files successfully")
```

### Workflow 4: Research Data Collection

```python
import pandas as pd

# Process and collect data
data = []
for ecg_file in ecg_files:
    try:
        result = converter.convert(ecg_file)
        
        data.append({
            'file': ecg_file,
            'heart_rate': result.intervals.heart_rate,
            'qrs_duration': result.intervals.qrs_duration,
            'qt_interval': result.intervals.qt_interval,
            'quality': result.quality_metrics.overall_quality
        })
    except Exception as e:
        print(f"Failed {ecg_file}: {e}")

# Create dataset
df = pd.DataFrame(data)
df.to_csv('ecg_dataset.csv', index=False)
```

## Configuration

### Environment Variables

Create a `.env` file:

```bash
# Application
ENV=production
DEBUG=false
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Processing
DEFAULT_PAPER_SPEED=25.0
DEFAULT_GAIN=10.0
MAX_UPLOAD_SIZE_MB=50

# Models
MODEL_DIR=./models
USE_GPU=true

# Security
API_KEY=your-secret-key
CORS_ORIGINS=["http://localhost:3000"]
```

### Python Configuration

```python
from ecg2signal.config import Settings

settings = Settings(
    default_paper_speed=50.0,  # 50 mm/s
    default_gain=5.0,           # 5 mm/mV (double standard)
    use_gpu=True,
    max_image_size=4096
)

converter = ECGConverter(settings)
```

## Performance Optimization

### GPU Acceleration

```python
# Enable GPU processing
settings = Settings(use_gpu=True, gpu_device=0)
converter = ECGConverter(settings)

# Batch processing on GPU
results = converter.convert_batch(files, output_dir='out/')
```

### Parallel Processing

```python
from concurrent.futures import ProcessPoolExecutor

def process_file(filepath):
    converter = ECGConverter()
    return converter.convert(filepath)

# Process in parallel
with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_file, ecg_files))
```

### Caching

```python
# Enable result caching
settings = Settings(
    enable_cache=True,
    cache_dir='./cache',
    cache_max_size_gb=10.0
)
```

## Troubleshooting

### Issue: Model not found

```bash
# Generate demo models
python scripts/generate_demo_models.py

# Or download pre-trained (if available)
bash scripts/download_demo_models.sh
```

### Issue: Low quality results

```python
# Check quality metrics
result = converter.convert('ecg.jpg')
print(f"Quality: {result.quality_metrics.overall_quality}")
print(f"SNR: {result.quality_metrics.snr} dB")

# Try adjusting preprocessing
result = converter.convert(
    'ecg.jpg',
    paper_speed=50.0,  # Try different speed
    gain=5.0            # Try different gain
)
```

### Issue: Grid not detected

```python
# Manually specify calibration
result = converter.convert(
    'ecg.jpg',
    paper_speed=25.0,
    gain=10.0
    # Calibration will use these values directly
)
```

### Issue: API timeout

```bash
# Increase timeout for large files
uvicorn ecg2signal.api.main:app --timeout-keep-alive 300
```

## Next Steps

### 1. Training Custom Models

```bash
# Collect training data
# - Use PhysioNet datasets
# - Or generate synthetic data

# Train U-Net
python -m ecg2signal.training.train_unet \
    --config training/configs/unet_small.yaml

# Train layout detector
python -m ecg2signal.training.train_layout \
    --config training/configs/layout_cnn.yaml

# Train OCR
python -m ecg2signal.training.train_ocr \
    --config training/configs/ocr_tiny.yaml
```

### 2. Production Deployment

```bash
# Build production Docker image
docker build -f docker/Dockerfile -t ecg2signal:latest .

# Deploy with docker-compose
docker-compose -f docker/compose.yaml up -d

# Or deploy to Kubernetes
kubectl apply -f k8s/
```

### 3. Integration

```python
# Integrate with your application
from ecg2signal import ECGConverter

class ECGProcessor:
    def __init__(self):
        self.converter = ECGConverter()
    
    def process_patient_ecg(self, ecg_path, patient_id):
        result = self.converter.convert(ecg_path)
        
        # Save to database
        self.save_to_db(patient_id, result)
        
        # Notify if abnormal
        if self.is_abnormal(result):
            self.send_alert(patient_id, result)
        
        return result
```

## Resources

- **Documentation**: See `docs/` directory
- **API Docs**: http://localhost:8000/docs (when API is running)
- **Examples**: See `notebooks/` directory
- **Test Data**: PhysioNet (https://physionet.org/)
- **Support**: GitHub Issues

## Common Commands Reference

```bash
# Installation
pip install -r requirements.txt
python scripts/generate_demo_models.py

# Testing
pytest tests/
python validate_project.py

# Running
python -m ecg2signal.cli.ecg2signal convert input.jpg -o output/
uvicorn ecg2signal.api.main:app --reload
streamlit run ecg2signal/ui/app.py
jupyter notebook notebooks/complete_demo.ipynb

# Training
python -m ecg2signal.training.train_unet
python -m ecg2signal.training.train_layout
python -m ecg2signal.training.train_ocr

# Docker
docker-compose up
docker build -t ecg2signal .

# Development
pytest --cov=ecg2signal
ruff check .
black ecg2signal/
mypy ecg2signal/
```

## Getting Help

1. Check the documentation in `docs/`
2. Run the demo notebook: `notebooks/complete_demo.ipynb`
3. Review test cases in `tests/`
4. Check API docs at `/docs` endpoint
5. Open GitHub issue for bugs

---

**Ready to convert your first ECG?** Start with the demo notebook! 🎉
