
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
