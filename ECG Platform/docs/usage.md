
# Usage Guide

## CLI Usage

```bash
ecg2signal convert input.jpg --output ./results --format wfdb
```

## Python API

```python
from ecg2signal import ECGConverter

converter = ECGConverter()
result = converter.convert("ecg.jpg")
result.export_wfdb("output/")
```

## REST API

```bash
curl -X POST http://localhost:8000/convert -F "file=@ecg.jpg"
```
