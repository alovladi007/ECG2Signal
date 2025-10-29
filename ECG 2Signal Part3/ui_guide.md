# ECG2Signal Enhanced UI/UX Documentation

## Overview

The ECG2Signal Enhanced UI is a beautiful, production-ready Streamlit dashboard that provides:

- 🎨 **Modern Design**: Gradient colors, custom CSS, beautiful cards
- 📊 **Interactive Visualizations**: Plotly charts with zoom, pan, hover
- ⚡ **Real-time Progress**: Live progress bars with status updates
- 📁 **Multi-file Support**: Batch processing with queue management
- 📈 **Quality Metrics**: Gauges, charts, and detailed analysis
- 💾 **Multiple Exports**: CSV, JSON, WFDB, EDF, FHIR, DICOM
- 🔄 **Session Management**: Results history and comparison

## Features

### 1. Beautiful Interface

The UI features a modern, professional design with:

- **Gradient Headers**: Eye-catching colored gradients
- **Metric Cards**: Beautiful cards showing key metrics
- **Custom Styling**: Professional CSS for polished look
- **Responsive Layout**: Works on desktop and tablets
- **Color-coded Quality**: Green (good), yellow (warning), red (bad)

### 2. Real-time Processing

Watch your ECG convert in real-time:

```
📁 Saving file... (10%)
🖼️  Loading image... (20%)
🔄 Preprocessing... (30%)
📐 Detecting grid... (40%)
📍 Detecting lead layout... (50%)
✂️  Segmenting waveforms... (60%)
📊 Extracting signals... (75%)
❤️  Extracting clinical features... (85%)
✅ Assessing quality... (95%)
✨ Complete! (100%)
```

### 3. Interactive Visualizations

#### Signal Plots
- **Plotly Integration**: Zoom, pan, hover on signals
- **Multi-lead Display**: Select which leads to view
- **Time Navigation**: Explore different time ranges
- **Hover Information**: Precise time and amplitude values

#### Quality Gauges
- **Circular Gauges**: Visual quality indicators
- **Color Zones**: Red (bad), yellow (warning), green (good)
- **Threshold Lines**: Clear quality thresholds
- **Delta Indicators**: Comparison to target values

#### Clinical Charts
- **Bar Charts**: PR, QRS, QT, QTc intervals
- **Normal Ranges**: Visual bands showing normal values
- **Color Coding**: Green (normal), red (abnormal)
- **Hover Details**: Exact values and ranges

### 4. Sidebar Settings

Customizable processing options:

#### Calibration Settings
- **Paper Speed**: 10-100 mm/s (slider)
- **Gain**: 2.5-40 mm/mV (slider)
- **Tooltips**: Helpful hints for each setting

#### Analysis Options
- ☑️ Extract Clinical Intervals
- ☑️ Assess Signal Quality
- ☑️ Show Interactive Plots

#### Export Options
- Multiple format selection
- Quick export buttons
- Batch export support

### 5. Three-Tab Interface

#### Tab 1: Upload & Convert
- Drag-and-drop file upload
- Multi-file support
- Image preview
- Batch processing
- Progress tracking

#### Tab 2: Results
- Result selector dropdown
- Beautiful metric cards
- Interactive signal plots
- Quality dashboard
- Clinical intervals chart
- Export buttons

#### Tab 3: About
- Feature list
- Usage instructions
- Tips and tricks
- Version information

## Usage Guide

### Starting the UI

```bash
# Basic start
streamlit run ecg2signal/ui/app.py

# With options
streamlit run ecg2signal/ui/app.py --server.port 8501 --server.address 0.0.0.0

# Development mode (auto-reload)
streamlit run ecg2signal/ui/app.py --server.runOnSave true
```

### Converting ECGs

1. **Upload Files**
   - Click "Browse files" or drag & drop
   - Supports: JPG, PNG, TIFF, PDF
   - Multiple files allowed

2. **Adjust Settings** (optional)
   - Set paper speed (default: 25 mm/s)
   - Set gain (default: 10 mm/mV)
   - Toggle analysis options

3. **Convert**
   - Click "🚀 Convert All" button
   - Watch real-time progress
   - Celebrate with balloons! 🎈

4. **View Results**
   - Switch to "Results" tab
   - Select a result from dropdown
   - Explore interactive plots
   - Check quality metrics

5. **Export Data**
   - Choose export format(s)
   - Click download button
   - Save to your computer

### Keyboard Shortcuts

- `r` - Rerun the app
- `Ctrl+Shift+R` - Clear cache and rerun
- `Ctrl+Enter` - Run selected cell (in input)

## Customization

### Changing Colors

Edit the CSS in `app.py`:

```python
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #YOUR_COLOR_1, #YOUR_COLOR_2);
    }
    .metric-card {
        background: linear-gradient(135deg, #YOUR_COLOR_3, #YOUR_COLOR_4);
    }
</style>
""", unsafe_allow_html=True)
```

### Adding Custom Metrics

Add new metric cards:

```python
with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Your Metric</div>
        <div class="metric-value">{}</div>
    </div>
    """.format(your_value), unsafe_allow_html=True)
```

### Custom Plots

Create new visualization functions in `viz.py`:

```python
def create_your_plot(data):
    fig = go.Figure()
    # Add your traces
    return fig
```

Then use in app:

```python
fig = create_your_plot(data)
st.plotly_chart(fig, use_container_width=True)
```

## Performance Tips

### Caching

Use Streamlit caching for expensive operations:

```python
@st.cache_resource
def load_model():
    return ECGConverter()

@st.cache_data
def process_data(data):
    return expensive_operation(data)
```

### Large Files

For large files:

```python
# Limit preview size
MAX_PREVIEW_SIZE = 5 * 1024 * 1024  # 5 MB

if uploaded_file.size < MAX_PREVIEW_SIZE:
    st.image(uploaded_file)
else:
    st.info("File too large for preview")
```

### Batch Processing

Process files in chunks:

```python
BATCH_SIZE = 5

for i in range(0, len(files), BATCH_SIZE):
    batch = files[i:i+BATCH_SIZE]
    results = process_batch(batch)
```

## Deployment

### Local Deployment

```bash
# Development
streamlit run app.py

# Production (with more workers)
streamlit run app.py --server.maxUploadSize 200
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "ecg2signal/ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t ecg2signal-ui .
docker run -p 8501:8501 ecg2signal-ui
```

### Cloud Deployment

#### Streamlit Cloud
1. Push to GitHub
2. Go to share.streamlit.io
3. Connect repository
4. Deploy!

#### Heroku
```bash
# Create Procfile
echo "web: streamlit run ecg2signal/ui/app.py --server.port=$PORT" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

#### AWS/GCP/Azure
Use Docker container with Kubernetes or App Service

## Troubleshooting

### Issue: App is slow

**Solution**: Enable caching

```python
@st.cache_resource
def init_converter():
    return ECGConverter()
```

### Issue: Large files crash

**Solution**: Set upload limit

```bash
streamlit run app.py --server.maxUploadSize 500
```

### Issue: Plots don't render

**Solution**: Check Plotly installation

```bash
pip install plotly --upgrade
```

### Issue: CSS not applying

**Solution**: Use `unsafe_allow_html=True`

```python
st.markdown("<style>...</style>", unsafe_allow_html=True)
```

## API Reference

### Session State Variables

```python
st.session_state.results  # List of conversion results
st.session_state.converter  # ECGConverter instance
```

### Key Functions

#### `init_converter()`
Initialize and cache the ECG converter.

#### `process_ecg(uploaded_file, paper_speed, gain, ...)`
Process ECG with progress tracking.

**Returns**: Dictionary with result and filename

#### `create_signal_plot(signals, fs)`
Create interactive signal visualization.

**Returns**: Plotly figure

#### `create_quality_gauge(quality_score)`
Create quality gauge chart.

**Returns**: Plotly figure

#### `create_intervals_chart(intervals)`
Create clinical intervals bar chart.

**Returns**: Plotly figure

## Examples

### Example 1: Basic Conversion

```python
# Upload file through UI
# Adjust settings if needed
# Click "Convert All"
# View results in Results tab
```

### Example 2: Batch Processing

```python
# Upload multiple files
# All files converted automatically
# Compare results in Results tab
```

### Example 3: Quality Analysis

```python
# Enable "Assess Signal Quality"
# Convert ECG
# View quality dashboard
# Check SNR, baseline, coverage
```

### Example 4: Export to FHIR

```python
# Select FHIR in export formats
# Convert ECG
# Go to Results tab
# Click "Download JSON"
# JSON contains FHIR Observation
```

## Best Practices

### 1. Image Quality
- Use high-resolution scans (300+ DPI)
- Ensure good contrast
- Avoid excessive noise

### 2. Calibration
- Double-check paper speed (usually 25 mm/s)
- Verify gain setting (usually 10 mm/mV)
- These vary by country/institution

### 3. Quality Checking
- Always enable quality assessment
- Check quality score > 80%
- Verify SNR > 20 dB

### 4. Clinical Validation
- Compare extracted intervals with original
- Verify heart rate is reasonable
- Check for clipping or drift

### 5. Export Format
- Use WFDB for research
- Use FHIR for EHR integration
- Use CSV for analysis
- Use DICOM for archiving

## Advanced Features

### Custom Themes

Create `config.toml`:

```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### Custom Components

Create reusable components:

```python
def quality_card(quality):
    color = "green" if quality > 0.8 else "yellow" if quality > 0.6 else "red"
    st.markdown(f"""
    <div style="background-color: {color}; padding: 20px; border-radius: 10px;">
        <h2>Quality: {quality:.0%}</h2>
    </div>
    """, unsafe_allow_html=True)
```

### Multi-page App

Create `pages/` directory:

```
ecg2signal/ui/
├── app.py (main page)
└── pages/
    ├── 1_Upload.py
    ├── 2_Results.py
    └── 3_Settings.py
```

## Support

For issues or questions:

1. Check this documentation
2. Review the demo in `notebooks/`
3. Check the FAQ in `docs/`
4. Open an issue on GitHub

## Version History

### Version 1.0.0 (Current)
- Beautiful gradient design
- Real-time progress tracking
- Interactive Plotly charts
- Multi-file support
- Quality dashboard
- Clinical intervals chart
- Multiple export formats
- Session management

### Planned Features
- Batch comparison view
- PDF report generation
- Advanced filtering options
- User preferences
- Cloud storage integration
- Collaborative annotations

---

**Have fun with the Enhanced UI! ❤️**
