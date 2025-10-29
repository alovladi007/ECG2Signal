
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
