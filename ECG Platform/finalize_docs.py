#!/usr/bin/env python3
from pathlib import Path

docs = {
"docs/api.md": '''
# API Reference

## REST API Endpoints

### POST /convert
Convert ECG image to signals.

**Parameters:**
- `file`: Image or PDF file
- `format`: Export format (wfdb, edf, json, csv)
- `paper_speed`: Paper speed in mm/s (default: 25)
- `gain`: Gain in mm/mV (default: 10)

**Response:**
```json
{
  "status": "success",
  "format": "wfdb",
  "quality_score": 0.92
}
```

### GET /health
Health check endpoint.

## Python API

### ECGConverter

Main class for ECG conversion.

```python
converter = ECGConverter(settings)
result = converter.convert("ecg.jpg")
```

### ECGResult

Result object with signals and metadata.

**Properties:**
- `signals`: dict[str, np.ndarray] - Signal data
- `sample_rate`: int - Sampling rate
- `quality_metrics`: QualityMetrics
- `intervals`: Intervals

**Methods:**
- `export_wfdb(output_dir)` 
- `export_edf(output_path)`
- `export_json(output_path)`
- `export_csv(output_dir)`
''',

"docs/models.md": '''
# Model Architecture

## U-Net Segmentation

Separates ECG waveforms from grid and text.

**Architecture:**
- Encoder: 4 downsampling blocks
- Decoder: 4 upsampling blocks
- Skip connections
- Output: 3-channel mask (grid, waveform, text)

## Transformer OCR

Extracts text labels and metadata.

**Features:**
- Lead name recognition
- Paper speed detection
- Gain detection
- Patient metadata extraction

## Layout CNN

Detects 12-lead panel positions.

**Output:**
- Bounding boxes for 12 leads
- Rhythm strip detection
- Layout type classification
''',

"docs/data_spec.md": '''
# Data Specifications

## Input Formats

### Images
- JPEG, PNG, TIFF
- RGB or grayscale
- Recommended: 300 DPI
- Max size: 4096x4096 pixels

### PDF
- Single or multi-page
- Extracted at 300 DPI
- First page used by default

## Output Formats

### WFDB (MIT/PhysioNet)
- `.dat`: Binary signal data
- `.hea`: ASCII header
- 16-bit ADC resolution
- 1000 units per mV

### EDF+ (European Data Format)
- Standard clinical format
- Full metadata support
- Compatible with EEG software

### FHIR (HL7 Standard)
- JSON format
- Observation resource
- SampledData type
- LOINC codes

### DICOM Waveform
- SOP Class: 12-Lead ECG
- SNOMED CT codes
- Full patient metadata
''',

"docs/calibration.md": '''
# Calibration Guide

## Paper Settings

### Standard Settings

**25 mm/s, 10 mm/mV** (Most Common)
- 1 small square (1mm) = 0.04s horizontally
- 1 small square = 0.1mV vertically

**50 mm/s, 5 mm/mV** (Fast Recording)
- 1 small square = 0.02s
- 1 small square = 0.2mV

## Grid Detection

The system automatically detects:
- Major grid lines (5mm spacing)
- Minor grid lines (1mm spacing)
- Grid angle/rotation
- Pixels per millimeter

## Calibration Accuracy

Expected accuracy:
- Time: ±2%
- Voltage: ±3%
- Sample rate: Exact

## Manual Override

```python
result = converter.convert(
    "ecg.jpg",
    paper_speed=50.0,  # Override
    gain=5.0           # Override
)
```
''',

"docs/clinical_metrics.md": '''
# Clinical Metrics

## Interval Measurements

### Heart Rate
- Calculated from RR intervals
- Normal: 60-100 BPM

### PR Interval
- Start of P wave to start of QRS
- Normal: 120-200 ms

### QRS Duration
- Width of QRS complex
- Normal: <120 ms

### QT/QTc Interval
- Q wave to end of T wave
- QTc: Corrected for heart rate
- Normal QTc: <450 ms

## Quality Metrics

### SNR (Signal-to-Noise Ratio)
- Measures signal clarity
- Good: >20 dB
- Acceptable: >10 dB

### Baseline Drift
- Measures low-frequency wandering
- Good: <0.1
- Acceptable: <0.3

### Clipping Ratio
- Fraction of saturated samples
- Good: <0.01
- Acceptable: <0.05

### Coverage
- Fraction of valid signal
- Required: >0.8
''',

"docs/compliance_security.md": '''
# Compliance & Security

## Privacy

- **No external API calls**: All processing is local
- **No data transmission**: Data never leaves your infrastructure
- **No logging of PHI**: Patient data not logged
- **Temporary file cleanup**: Automatic cleanup of temp files

## HIPAA Compliance

The system is designed for HIPAA-compliant deployment:

1. Deploy on-premises or in private cloud
2. Enable audit logging
3. Encrypt data at rest
4. Use HTTPS for API
5. Implement access controls

## Security Best Practices

1. Use API keys for authentication
2. Enable CORS restrictions
3. Set maximum upload sizes
4. Validate all inputs
5. Regular security audits

## Data Retention

Configure data retention:

```python
settings.retain_input_images = False  # Don't keep inputs
settings.audit_logging = True         # Log operations
```

## Standards Compliance

- HL7 FHIR R4
- DICOM Part 10
- SCP-ECG (EN 1064)
- WFDB/PhysioNet
- EDF+ (European Data Format)
''',

"docs/roadmap.md": '''
# Roadmap

## Version 0.2 (Q2 2025)

- [ ] Real-time processing
- [ ] Batch optimization
- [ ] GPU acceleration
- [ ] Model fine-tuning tools
- [ ] Extended format support

## Version 0.3 (Q3 2025)

- [ ] AI-powered interpretation
- [ ] Anomaly detection
- [ ] Rhythm analysis
- [ ] Arrhythmia classification
- [ ] Report generation

## Version 1.0 (Q4 2025)

- [ ] FDA clearance preparation
- [ ] Clinical validation
- [ ] Multi-language support
- [ ] Mobile apps
- [ ] Cloud deployment

## Feature Requests

Submit feature requests on GitHub Issues.
''',

"CONTRIBUTING.md": '''
# Contributing to ECG2Signal

We welcome contributions! Here's how to get started:

## Development Setup

```bash
git clone https://github.com/yourusername/ecg2signal.git
cd ecg2signal
pip install -e ".[dev]"
pre-commit install
```

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Add tests for new features

## Testing

```bash
pytest tests/ -v --cov
```

## Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a PR

## Code Review

All PRs require:
- Passing tests
- Code review approval
- Documentation updates

## License

By contributing, you agree to license your contributions under Apache 2.0.
''',

}

for path, content in docs.items():
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content)
    print(f"Created {path}")

print(f"\n✓ Documentation complete ({len(docs)} files)")

