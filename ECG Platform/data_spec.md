
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
