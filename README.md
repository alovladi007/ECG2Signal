# ECG2Signal

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-production--ready-green.svg)](https://github.com/alovladi007/ECG2Signal)

**AI-Powered ECG Image to Signal Conversion with Advanced Clinical Analysis**

Transform ECG images (scans, photos, PDFs) into calibrated digital signals with comprehensive arrhythmia detection, QT analysis, and automated clinical interpretation.

![ECG2Signal Demo](https://img.shields.io/badge/demo-available-brightgreen)

## 🚀 Quick Start

The main project is located in the **[ECG Platform](ECG%20Platform/)** directory.

```bash
cd "ECG Platform"
pip install -e .
streamlit run ecg2signal/ui/app.py
```

## ✨ Key Features

### Core Capabilities
- 📸 Multi-format input (JPG, PNG, TIFF, PDF, mobile photos)
- 🧠 AI/ML pipeline (U-Net, Transformer OCR, CNN)
- 📊 12-lead ECG support with automatic detection
- ⚡ Beautiful Streamlit UI with real-time processing
- 🔌 REST API + CLI + Web interface

### Advanced Clinical Analysis (NEW)
- 🫀 **13 Arrhythmia Types**: AF, VT, VFib, SVT, bradycardia, AV blocks, PVCs, PACs
- 📊 **QT Analysis**: 4 correction formulas (Bazett, Fridericia, Framingham, Hodges)
- 🔍 **Automated Interpretation**: 8 clinical domains with evidence-based findings
- 📄 **Professional Reports**: Multi-page PDF reports with quality metrics

### Export Formats
- WFDB (PhysioNet) • EDF+ • HL7 FHIR • DICOM • JSON • CSV

## 📂 Repository Structure

```
ECG2Signal/
├── ECG Platform/          ⭐ Main project (start here!)
│   ├── ecg2signal/        # Python package (11 subpackages)
│   │   ├── api/          # FastAPI REST API
│   │   ├── ui/           # Streamlit dashboard (633 lines)
│   │   ├── clinical/     # Arrhythmia, QT, interpretation
│   │   ├── io/           # WFDB, EDF, FHIR, DICOM formats
│   │   ├── preprocess/   # Image processing
│   │   ├── segment/      # U-Net segmentation
│   │   └── ...           # 5 more subpackages
│   ├── tests/            # Comprehensive test suite
│   ├── docs/             # Full documentation
│   ├── notebooks/        # Interactive demos
│   └── README.md         # Complete documentation
│
├── ECG 2Signal Additional Features/
│   └── Clinical analysis modules (Option E)
│
├── ECG 2Signal Part 2/
│   └── Demo files and setup scripts
│
└── ECG 2Signal Part3/
    └── Enhanced UI components (Option C)
```

## 🎯 Getting Started

### 1. Navigate to Main Project

```bash
cd "ECG Platform"
```

### 2. Install Dependencies

```bash
pip install -e .
```

### 3. Launch Dashboard

```bash
streamlit run ecg2signal/ui/app.py
# Opens at http://localhost:8501
```

### 4. Or Start API Server

```bash
uvicorn ecg2signal.api.main:app --reload
# API docs at http://localhost:8000/docs
```

## 📖 Documentation

- **[Complete README](ECG%20Platform/README.md)** - Full documentation with usage examples
- **[Quick Start Guide](ECG%20Platform/QUICKSTART.md)** - Get started in 5 minutes
- **[Clinical Features](ECG%20Platform/CLINICAL_FEATURES_ADDED.md)** - Arrhythmia & QT analysis
- **[Demo Integration](ECG%20Platform/DEMO_INTEGRATION.md)** - Interactive notebooks
- **[Enhanced UI Guide](ECG%20Platform/docs/ui_guide.md)** - Streamlit dashboard

## 💻 Usage Example

```python
from ecg2signal import ECGConverter
from ecg2signal.clinical import detect_arrhythmias, analyze_qt

# Convert ECG image
converter = ECGConverter()
result = converter.convert("ecg_image.jpg", paper_speed=25.0, gain=10.0)

# Clinical analysis
arrhythmias = detect_arrhythmias(result.signals, result.sample_rate)
qt_analysis = analyze_qt(result.signals, result.sample_rate, gender='male')

print(f"Rhythm: {arrhythmias.primary_rhythm}")
print(f"QTc: {qt_analysis.qtc_bazett:.0f} ms - {qt_analysis.risk_level}")

# Export
result.export_wfdb("output/", "patient_001")
result.export_fhir("patient_123", "output/ecg.json")
```

## 🫀 Clinical Features Highlights

### Arrhythmia Detection
Detects 13 types with confidence scoring:
- **Critical**: VFib, VT, Complete Heart Block, Asystole
- **Common**: AF, Atrial Flutter, SVT, PVCs, PACs
- **Rate**: Sinus Bradycardia, Sinus Tachycardia
- **Conduction**: 1st/2nd Degree AV Block

### QT Interval Analysis
- 4 correction formulas for accuracy
- Gender-specific risk thresholds
- Drug interaction warnings
- QT dispersion analysis

### Automated Interpretation
Evidence-based findings across 8 domains:
- Rhythm • Rate • Intervals • Axis
- Morphology • Ischemia • Hypertrophy • Quality

## 🎨 Beautiful Web Interface

Launch the Streamlit dashboard to access:
- 🎨 Gradient design with custom CSS
- 📤 Drag-and-drop file upload
- 📊 Interactive Plotly visualizations
- 🎯 Real-time progress tracking
- 💾 Multiple export formats
- ✨ Quality metrics dashboard

## 📊 Project Stats

- **~17,000+ lines** of production code
- **100+ files** professionally organized
- **59 dependencies** for complete functionality
- **13 arrhythmia types** detection
- **4 QT correction** formulas
- **8 clinical domains** interpretation
- **6 export formats** supported

## 🔒 Privacy & Security

- ✅ Runs entirely locally
- ✅ No external API calls
- ✅ HIPAA-compliant deployment ready
- ✅ No data leaves your infrastructure

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](ECG%20Platform/CONTRIBUTING.md) for guidelines.

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with PyTorch, FastAPI, Streamlit, OpenCV, and clinical standards (WFDB, EDF+, FHIR, DICOM).

---

### 🌟 Quick Links

- **[📖 Full Documentation](ECG%20Platform/README.md)** - Complete guide
- **[🚀 Quick Start](ECG%20Platform/QUICKSTART.md)** - 5-minute setup
- **[🎨 Live Demo](ECG%20Platform/notebooks/complete_demo.ipynb)** - Interactive notebook
- **[🫀 Clinical Features](ECG%20Platform/CLINICAL_FEATURES_ADDED.md)** - Advanced analysis
- **[🐛 Issues](https://github.com/alovladi007/ECG2Signal/issues)** - Report bugs

---

**Made with ❤️ for clinicians, researchers, and developers**

*Transform ECG images into actionable clinical insights*
