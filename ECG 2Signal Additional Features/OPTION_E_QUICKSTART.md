# Option E: Clinical Features - Quick Start Guide

Get started with advanced clinical analysis in 5 minutes! 🚀

## Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "from ecg2signal.clinical import ArrhythmiaDetector; print('✅ Clinical features ready!')"
```

## Quick Examples

### 1. Basic Arrhythmia Detection (30 seconds)

```python
from ecg2signal import ECGConverter
from ecg2signal.clinical import ArrhythmiaDetector

# Convert ECG
converter = ECGConverter()
result = converter.convert('ecg_image.jpg')

# Detect arrhythmias
detector = ArrhythmiaDetector(sample_rate=result.sample_rate)
report = detector.detect(result.signals)

# Check results
print(f"Primary Rhythm: {report.primary_rhythm.value}")
print(f"Heart Rate: {report.heart_rate_mean:.0f} ± {report.heart_rate_std:.0f} BPM")

if report.critical_findings:
    print("\n⚠️ CRITICAL FINDINGS:")
    for finding in report.critical_findings:
        print(f"  • {finding}")
```

### 2. QT Interval Analysis (30 seconds)

```python
from ecg2signal import ECGConverter
from ecg2signal.clinical import QTAnalyzer

# Convert ECG
converter = ECGConverter()
result = converter.convert('ecg_image.jpg')

# Analyze QT
qt_analyzer = QTAnalyzer(sample_rate=result.sample_rate)
analysis = qt_analyzer.analyze(
    result.signals,
    r_peaks=None,  # Auto-detect
    gender='F'  # Female patient
)

# Check results
print(f"QTc: {analysis.mean_qtc:.0f} ms")
print(f"Risk: {analysis.risk_level.value.upper()}")

if analysis.is_prolonged:
    print("\n⚠️ QT PROLONGATION DETECTED")
    print("\nAvoid these medications:")
    for drug in analysis.drug_interactions[:3]:
        print(f"  • {drug}")
```

### 3. Complete Clinical Analysis (1 minute)

```python
from ecg2signal import ECGConverter
from ecg2signal.clinical import (
    ArrhythmiaDetector,
    QTAnalyzer,
    ClinicalInterpreter
)

# Convert ECG
converter = ECGConverter()
result = converter.convert('ecg_image.jpg')

# Run all analyses
arrhythmia_detector = ArrhythmiaDetector(result.sample_rate)
arrhythmia = arrhythmia_detector.detect(result.signals)

qt_analyzer = QTAnalyzer(result.sample_rate)
qt_analysis = qt_analyzer.analyze(result.signals, r_peaks=None, gender='M')

interpreter = ClinicalInterpreter()
findings = interpreter.interpret(
    signals=result.signals,
    sample_rate=result.sample_rate,
    intervals=result.intervals,
    quality=result.quality_metrics,
    arrhythmia=arrhythmia,
    qt_analysis=qt_analysis,
    patient_age=65,
    patient_gender='M'
)

# Print summary
print("="*50)
print("CLINICAL SUMMARY")
print("="*50)
print(f"\nPrimary Diagnosis: {findings.conclusion.primary_diagnosis}")
print(f"Severity: {findings.conclusion.severity.value.upper()}")

if findings.conclusion.urgent_action_required:
    print("\n⚠️ URGENT ACTION REQUIRED")

print("\nRecommendations:")
for i, rec in enumerate(findings.conclusion.recommendations, 1):
    print(f"  {i}. {rec}")

print(f"\nFollow-up: {findings.conclusion.follow_up}")
```

### 4. Generate Professional PDF Report (30 seconds)

```python
from ecg2signal import ECGConverter
from ecg2signal.clinical import (
    ArrhythmiaDetector,
    QTAnalyzer,
    ClinicalInterpreter,
    generate_pdf_report
)

# Convert and analyze
converter = ECGConverter()
result = converter.convert('ecg_image.jpg')

detector = ArrhythmiaDetector(result.sample_rate)
arrhythmia = detector.detect(result.signals)

qt_analyzer = QTAnalyzer(result.sample_rate)
qt_analysis = qt_analyzer.analyze(result.signals, r_peaks=None, gender='F')

interpreter = ClinicalInterpreter()
findings = interpreter.interpret(
    signals=result.signals,
    sample_rate=result.sample_rate,
    intervals=result.intervals,
    quality=result.quality_metrics,
    arrhythmia=arrhythmia,
    qt_analysis=qt_analysis,
    patient_age=58,
    patient_gender='F'
)

# Generate PDF report
generate_pdf_report(
    ecg_result=result,
    output_path='clinical_report.pdf',
    arrhythmia_report=arrhythmia,
    qt_analysis=qt_analysis,
    automated_findings=findings,
    patient_name='Jane Doe',
    patient_age=58,
    patient_gender='F',
    institution='Cardiology Clinic'
)

print("✅ Report generated: clinical_report.pdf")
```

## Common Workflows

### Workflow 1: Emergency Department Triage

```python
def triage_ecg(ecg_path):
    """Quick triage for emergency ECGs."""
    converter = ECGConverter()
    result = converter.convert(ecg_path)
    
    # Quick arrhythmia check
    detector = ArrhythmiaDetector(result.sample_rate)
    arrhythmia = detector.detect(result.signals)
    
    # Check for life-threatening conditions
    life_threatening = [
        'ventricular_fibrillation',
        'ventricular_tachycardia',
        'third_degree_av_block'
    ]
    
    if arrhythmia.primary_rhythm.value in life_threatening:
        return {
            'urgency': 'CRITICAL',
            'action': 'IMMEDIATE INTERVENTION',
            'rhythm': arrhythmia.primary_rhythm.value,
            'critical_findings': arrhythmia.critical_findings
        }
    
    return {
        'urgency': 'ROUTINE',
        'action': 'Standard workup',
        'rhythm': arrhythmia.primary_rhythm.value
    }

# Usage
triage = triage_ecg('patient_ecg.jpg')
print(f"Urgency: {triage['urgency']}")
print(f"Action: {triage['action']}")
```

### Workflow 2: Drug Safety Screening

```python
def check_qt_safety(ecg_path, patient_gender):
    """Screen for QT prolongation before prescribing medications."""
    converter = ECGConverter()
    result = converter.convert(ecg_path)
    
    qt_analyzer = QTAnalyzer(result.sample_rate)
    analysis = qt_analyzer.analyze(
        result.signals,
        r_peaks=None,
        gender=patient_gender
    )
    
    if analysis.is_prolonged:
        return {
            'safe_to_prescribe': False,
            'qtc': analysis.mean_qtc,
            'risk': analysis.risk_level.value,
            'avoid_drugs': analysis.drug_interactions,
            'recommendations': analysis.clinical_notes
        }
    
    return {
        'safe_to_prescribe': True,
        'qtc': analysis.mean_qtc,
        'risk': 'low'
    }

# Usage
safety = check_qt_safety('ecg.jpg', 'F')
if not safety['safe_to_prescribe']:
    print("⚠️ CAUTION: QT prolongation detected")
    print(f"QTc: {safety['qtc']:.0f} ms")
    print("\nAvoid prescribing:")
    for drug in safety['avoid_drugs'][:5]:
        print(f"  • {drug}")
```

### Workflow 3: Batch ECG Screening

```python
from pathlib import Path
import pandas as pd

def screen_ecg_batch(ecg_directory, output_csv='screening_results.csv'):
    """Screen multiple ECGs and generate summary report."""
    results = []
    
    for ecg_file in Path(ecg_directory).glob('*.jpg'):
        try:
            # Convert
            converter = ECGConverter()
            result = converter.convert(str(ecg_file))
            
            # Analyze
            detector = ArrhythmiaDetector(result.sample_rate)
            arrhythmia = detector.detect(result.signals)
            
            qt_analyzer = QTAnalyzer(result.sample_rate)
            qt_analysis = qt_analyzer.analyze(result.signals, r_peaks=None)
            
            # Store results
            results.append({
                'file': ecg_file.name,
                'rhythm': arrhythmia.primary_rhythm.value,
                'heart_rate': arrhythmia.heart_rate_mean,
                'qtc': qt_analysis.mean_qtc,
                'qt_risk': qt_analysis.risk_level.value,
                'abnormal': len(arrhythmia.critical_findings) > 0,
                'critical_findings': ', '.join(arrhythmia.critical_findings)
            })
            
        except Exception as e:
            results.append({
                'file': ecg_file.name,
                'error': str(e)
            })
    
    # Save to CSV
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    
    # Print summary
    print(f"Processed {len(results)} ECGs")
    print(f"Abnormal: {df['abnormal'].sum()} ({df['abnormal'].sum()/len(df)*100:.1f}%)")
    
    return df

# Usage
results = screen_ecg_batch('ecg_batch/', 'results.csv')
print(results.head())
```

### Workflow 4: Research Dataset Analysis

```python
def analyze_research_dataset(ecg_files, patient_data):
    """Comprehensive analysis for research purposes."""
    analyses = []
    
    for ecg_file, patient_info in zip(ecg_files, patient_data):
        converter = ECGConverter()
        result = converter.convert(ecg_file)
        
        # Full analysis
        detector = ArrhythmiaDetector(result.sample_rate)
        arrhythmia = detector.detect(result.signals)
        
        qt_analyzer = QTAnalyzer(result.sample_rate)
        qt_analysis = qt_analyzer.analyze(
            result.signals,
            r_peaks=None,
            gender=patient_info['gender']
        )
        
        interpreter = ClinicalInterpreter()
        findings = interpreter.interpret(
            signals=result.signals,
            sample_rate=result.sample_rate,
            intervals=result.intervals,
            quality=result.quality_metrics,
            arrhythmia=arrhythmia,
            qt_analysis=qt_analysis,
            patient_age=patient_info['age'],
            patient_gender=patient_info['gender']
        )
        
        analyses.append({
            'patient_id': patient_info['id'],
            'arrhythmia': arrhythmia,
            'qt_analysis': qt_analysis,
            'findings': findings
        })
    
    return analyses
```

## Tips & Tricks

### 1. Improve Arrhythmia Detection Accuracy

```python
# Pre-filter the signal for better R-peak detection
from scipy.signal import butter, filtfilt

def preprocess_for_arrhythmia(signal, sample_rate):
    # Bandpass 0.5-40 Hz
    nyquist = sample_rate / 2
    low = 0.5 / nyquist
    high = 40 / nyquist
    b, a = butter(2, [low, high], btype='band')
    filtered = filtfilt(b, a, signal)
    return filtered

# Use preprocessed signal
preprocessed = {
    name: preprocess_for_arrhythmia(sig, sample_rate)
    for name, sig in result.signals.items()
}

detector = ArrhythmiaDetector(sample_rate)
arrhythmia = detector.detect(preprocessed)
```

### 2. Custom QT Normal Ranges

```python
# Adjust thresholds for specific populations
class CustomQTAnalyzer(QTAnalyzer):
    # Athletes have different normal ranges
    NORMAL_QTC_MALE = (340, 460)  # Extended for athletes
    NORMAL_QTC_FEMALE = (340, 480)

analyzer = CustomQTAnalyzer(sample_rate=500)
analysis = analyzer.analyze(signals, r_peaks, gender='M')
```

### 3. Filter Non-Confident Findings

```python
# Only show high-confidence findings
high_confidence_findings = [
    f for f in findings.findings
    if f.confidence > 0.75
]

for finding in high_confidence_findings:
    print(f"{finding.name} ({finding.confidence:.0%} confidence)")
    print(f"  {finding.description}")
```

### 4. Export to JSON for Integration

```python
import json

# Convert findings to JSON
findings_dict = {
    'primary_diagnosis': findings.conclusion.primary_diagnosis,
    'severity': findings.conclusion.severity.value,
    'urgent': findings.conclusion.urgent_action_required,
    'recommendations': findings.conclusion.recommendations,
    'arrhythmia': {
        'rhythm': arrhythmia.primary_rhythm.value,
        'heart_rate': arrhythmia.heart_rate_mean,
        'critical': arrhythmia.critical_findings
    },
    'qt': {
        'qtc': qt_analysis.mean_qtc,
        'risk': qt_analysis.risk_level.value,
        'prolonged': qt_analysis.is_prolonged
    }
}

with open('analysis.json', 'w') as f:
    json.dump(findings_dict, f, indent=2)
```

## Troubleshooting

### Issue: No R-peaks detected

```python
# Solution: Check signal quality and adjust peak detection
detector = ArrhythmiaDetector(sample_rate)
detector.min_rr_interval = int(0.25 * sample_rate)  # Lower threshold
detector.max_rr_interval = int(2.5 * sample_rate)   # Higher threshold
```

### Issue: QT measurements seem wrong

```python
# Solution: Manually inspect T-wave detection
qt_analyzer = QTAnalyzer(sample_rate)
measurements = qt_analyzer._measure_qt_intervals(signal, r_peaks, 'II')

# Check individual measurements
for m in measurements:
    if m.measurement_quality < 0.7:
        print(f"Low quality measurement at {m.rr_interval} ms RR")
```

### Issue: Too many false positives

```python
# Solution: Increase confidence threshold
detector = ArrhythmiaDetector(sample_rate)
detector.confidence_threshold = 0.75  # Default is 0.6

# Or filter after detection
reliable_detections = [
    d for d in arrhythmia.detections
    if d.confidence > 0.75
]
```

## Performance Tips

1. **Batch Processing**: Process multiple ECGs in parallel
   ```python
   from concurrent.futures import ProcessPoolExecutor
   
   with ProcessPoolExecutor() as executor:
       results = list(executor.map(analyze_ecg, ecg_files))
   ```

2. **Caching**: Cache R-peak detection results
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def get_r_peaks(signal_hash):
       return detector._detect_r_peaks(signal)
   ```

3. **Partial Analysis**: Skip optional analyses if not needed
   ```python
   # Skip QT if normal rhythm
   if arrhythmia.primary_rhythm == ArrhythmiaType.NORMAL:
       qt_analysis = None  # Skip QT analysis
   ```

## Next Steps

1. **Read Full Documentation**: See `OPTION_E_CLINICAL_FEATURES.md`
2. **Try Examples**: Run the workflows above
3. **Generate Reports**: Create PDF reports for your data
4. **Validate Results**: Compare with manual interpretations
5. **Customize**: Extend detection algorithms for your needs

## Resources

- Full Documentation: `OPTION_E_CLINICAL_FEATURES.md`
- API Reference: See docstrings in source files
- Clinical Guidelines: ACC/AHA/ESC guidelines
- Validation Data: PhysioNet databases

---

**Happy Analyzing! 🎉**

Start with the basic examples and work your way up to complete workflows.
