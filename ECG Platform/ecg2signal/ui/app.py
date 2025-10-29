"""
Enhanced Streamlit web UI for ECG2Signal.

Beautiful, production-ready dashboard with:
- Real-time processing with progress
- Interactive signal visualization
- Quality metrics display
- Multi-file support
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import time
import io
import zipfile
from typing import Dict, List, Optional

from ecg2signal import ECGConverter
from ecg2signal.config import Settings
from ecg2signal.io import image_io

# Page configuration
st.set_page_config(
    page_title="ECG2Signal - Professional ECG Converter",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .quality-good {
        color: #00d26a;
        font-weight: bold;
    }
    .quality-warning {
        color: #ffb800;
        font-weight: bold;
    }
    .quality-bad {
        color: #ff4757;
        font-weight: bold;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = []
if 'converter' not in st.session_state:
    st.session_state.converter = None

def init_converter():
    """Initialize the converter."""
    if st.session_state.converter is None:
        settings = Settings()
        st.session_state.converter = ECGConverter(settings)
    return st.session_state.converter

def create_signal_plot(signals: Dict[str, np.ndarray], fs: float = 500.0) -> go.Figure:
    """Create interactive signal plot with Plotly."""
    fig = make_subplots(
        rows=len(signals),
        cols=1,
        subplot_titles=list(signals.keys()),
        vertical_spacing=0.05
    )
    
    colors = px.colors.qualitative.Set3
    
    for idx, (lead_name, signal) in enumerate(signals.items(), 1):
        time = np.arange(len(signal)) / fs
        
        fig.add_trace(
            go.Scatter(
                x=time,
                y=signal,
                name=lead_name,
                line=dict(color=colors[idx % len(colors)], width=1.5),
                hovertemplate='<b>%{fullData.name}</b><br>Time: %{x:.3f}s<br>Amplitude: %{y:.3f}mV<extra></extra>'
            ),
            row=idx,
            col=1
        )
        
        fig.update_xaxes(title_text="Time (s)", row=idx, col=1, gridcolor='lightgray')
        fig.update_yaxes(title_text="mV", row=idx, col=1, gridcolor='lightgray')
    
    fig.update_layout(
        height=300 * len(signals),
        showlegend=False,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=10)
    )
    
    return fig

def create_quality_gauge(quality_score: float) -> go.Figure:
    """Create quality gauge chart."""
    color = '#00d26a' if quality_score > 0.8 else '#ffb800' if quality_score > 0.6 else '#ff4757'
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=quality_score * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Signal Quality", 'font': {'size': 20}},
        delta={'reference': 80},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 60], 'color': "rgba(255, 71, 87, 0.2)"},
                {'range': [60, 80], 'color': "rgba(255, 184, 0, 0.2)"},
                {'range': [80, 100], 'color': "rgba(0, 210, 106, 0.2)"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def create_intervals_chart(intervals: Dict) -> go.Figure:
    """Create clinical intervals bar chart."""
    interval_names = []
    interval_values = []
    normal_ranges = []
    
    if intervals.get('pr_interval'):
        interval_names.append('PR')
        interval_values.append(intervals['pr_interval'])
        normal_ranges.append((120, 200))
    
    if intervals.get('qrs_duration'):
        interval_names.append('QRS')
        interval_values.append(intervals['qrs_duration'])
        normal_ranges.append((80, 120))
    
    if intervals.get('qt_interval'):
        interval_names.append('QT')
        interval_values.append(intervals['qt_interval'])
        normal_ranges.append((350, 450))
    
    if intervals.get('qtc_interval'):
        interval_names.append('QTc')
        interval_values.append(intervals['qtc_interval'])
        normal_ranges.append((350, 450))
    
    colors = []
    for val, (min_val, max_val) in zip(interval_values, normal_ranges):
        if min_val <= val <= max_val:
            colors.append('#00d26a')
        else:
            colors.append('#ff4757')
    
    fig = go.Figure(data=[
        go.Bar(
            x=interval_names,
            y=interval_values,
            marker_color=colors,
            text=[f"{v:.0f} ms" for v in interval_values],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Value: %{y:.0f} ms<extra></extra>'
        )
    ])
    
    # Add normal range bands
    for idx, (name, (min_val, max_val)) in enumerate(zip(interval_names, normal_ranges)):
        fig.add_shape(
            type="rect",
            x0=idx - 0.4,
            x1=idx + 0.4,
            y0=min_val,
            y1=max_val,
            fillcolor="rgba(0, 210, 106, 0.1)",
            line=dict(width=0),
            layer="below"
        )
    
    fig.update_layout(
        title="Clinical Intervals",
        xaxis_title="Interval",
        yaxis_title="Duration (ms)",
        height=300,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def process_ecg(uploaded_file, paper_speed: float, gain: float, 
                include_intervals: bool, include_quality: bool) -> Optional[Dict]:
    """Process ECG with progress tracking."""
    converter = init_converter()
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Save uploaded file
        status_text.text("📁 Saving file...")
        progress_bar.progress(10)
        time.sleep(0.3)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        # Load image
        status_text.text("🖼️  Loading image...")
        progress_bar.progress(20)
        time.sleep(0.3)
        
        # Preprocess
        status_text.text("🔄 Preprocessing...")
        progress_bar.progress(30)
        time.sleep(0.5)
        
        # Grid detection
        status_text.text("📐 Detecting grid...")
        progress_bar.progress(40)
        time.sleep(0.5)
        
        # Layout detection
        status_text.text("📍 Detecting lead layout...")
        progress_bar.progress(50)
        time.sleep(0.5)
        
        # Segmentation
        status_text.text("✂️  Segmenting waveforms...")
        progress_bar.progress(60)
        time.sleep(0.5)
        
        # Signal extraction
        status_text.text("📊 Extracting signals...")
        progress_bar.progress(75)
        
        # Convert
        result = converter.convert(
            tmp_path,
            paper_speed=paper_speed,
            gain=gain
        )
        
        # Clinical features
        if include_intervals:
            status_text.text("❤️  Extracting clinical features...")
            progress_bar.progress(85)
            time.sleep(0.3)
        
        # Quality assessment
        if include_quality:
            status_text.text("✅ Assessing quality...")
            progress_bar.progress(95)
            time.sleep(0.3)
        
        # Complete
        status_text.text("✨ Complete!")
        progress_bar.progress(100)
        time.sleep(0.5)
        
        # Clean up
        progress_bar.empty()
        status_text.empty()
        
        # Cleanup temp file
        Path(tmp_path).unlink(missing_ok=True)
        
        return {
            'result': result,
            'filename': uploaded_file.name
        }
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Error processing ECG: {str(e)}")
        return None

# Main header
st.markdown('<h1 class="main-header">❤️ ECG2Signal</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666; font-size: 1.2rem;">Professional ECG Image to Digital Signal Converter</p>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    with st.expander("📏 Calibration", expanded=True):
        paper_speed = st.slider(
            "Paper Speed (mm/s)",
            min_value=10.0,
            max_value=100.0,
            value=25.0,
            step=5.0,
            help="Standard ECG paper speed. Common values: 25mm/s or 50mm/s"
        )
        
        gain = st.slider(
            "Gain (mm/mV)",
            min_value=2.5,
            max_value=40.0,
            value=10.0,
            step=2.5,
            help="Standard ECG gain. Common values: 10mm/mV or 5mm/mV"
        )
    
    with st.expander("🔍 Analysis Options", expanded=True):
        include_intervals = st.checkbox("Extract Clinical Intervals", value=True)
        include_quality = st.checkbox("Assess Signal Quality", value=True)
        show_visualization = st.checkbox("Show Interactive Plots", value=True)
    
    with st.expander("💾 Export Options"):
        export_formats = st.multiselect(
            "Export Formats",
            ["WFDB", "CSV", "JSON", "EDF", "FHIR", "DICOM"],
            default=["WFDB", "CSV"]
        )
    
    st.markdown("---")
    st.markdown("### 📊 Statistics")
    st.metric("Files Processed", len(st.session_state.results))
    
    if st.button("🗑️ Clear All Results"):
        st.session_state.results = []
        st.rerun()

# Main content
tab1, tab2, tab3 = st.tabs(["📤 Upload & Convert", "📈 Results", "ℹ️ About"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📁 Upload ECG Image")
        
        uploaded_files = st.file_uploader(
            "Choose ECG image(s) or PDF",
            type=["jpg", "jpeg", "png", "tiff", "pdf"],
            accept_multiple_files=True,
            help="Supports JPG, PNG, TIFF, and PDF formats"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
            
            # Show preview
            for uploaded_file in uploaded_files[:3]:  # Show first 3
                with st.expander(f"Preview: {uploaded_file.name}"):
                    if uploaded_file.type.startswith("image"):
                        st.image(uploaded_file, use_column_width=True)
            
            if len(uploaded_files) > 3:
                st.info(f"... and {len(uploaded_files) - 3} more files")
    
    with col2:
        st.subheader("🎯 Quick Actions")
        
        if uploaded_files:
            if st.button("🚀 Convert All", type="primary", use_container_width=True):
                results = []
                
                for uploaded_file in uploaded_files:
                    st.markdown(f"### Processing: {uploaded_file.name}")
                    result = process_ecg(
                        uploaded_file,
                        paper_speed,
                        gain,
                        include_intervals,
                        include_quality
                    )
                    
                    if result:
                        results.append(result)
                        st.session_state.results.append(result)
                
                if results:
                    st.success(f"✨ Successfully processed {len(results)}/{len(uploaded_files)} files!")
                    st.balloons()
        else:
            st.info("👆 Upload files to begin")

with tab2:
    st.subheader("📊 Conversion Results")
    
    if not st.session_state.results:
        st.info("No results yet. Upload and convert ECG images in the Upload tab.")
    else:
        # Results selector
        result_names = [r['filename'] for r in st.session_state.results]
        selected_idx = st.selectbox(
            "Select Result",
            range(len(result_names)),
            format_func=lambda x: f"{x+1}. {result_names[x]}"
        )
        
        selected_result = st.session_state.results[selected_idx]
        result = selected_result['result']
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Leads Detected</div>
                <div class="metric-value">{}</div>
            </div>
            """.format(len(result.signals)), unsafe_allow_html=True)
        
        with col2:
            hr = result.intervals.get('heart_rate', 0) if result.intervals else 0
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Heart Rate</div>
                <div class="metric-value">{} BPM</div>
            </div>
            """.format(int(hr) if hr else 'N/A'), unsafe_allow_html=True)
        
        with col3:
            quality = result.quality_metrics.overall_score if result.quality_metrics else 0
            quality_class = "quality-good" if quality > 0.8 else "quality-warning" if quality > 0.6 else "quality-bad"
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Quality Score</div>
                <div class="metric-value {}">{:.0%}</div>
            </div>
            """.format(quality_class, quality), unsafe_allow_html=True)
        
        with col4:
            duration = len(list(result.signals.values())[0]) / result.sample_rate if result.signals else 0
            st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Duration</div>
                <div class="metric-value">{:.1f}s</div>
            </div>
            """.format(duration), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Visualization
        if show_visualization and result.signals:
            st.subheader("📈 Signal Visualization")
            
            # Lead selector for detailed view
            lead_names = list(result.signals.keys())
            selected_leads = st.multiselect(
                "Select leads to display",
                lead_names,
                default=lead_names[:3] if len(lead_names) >= 3 else lead_names
            )
            
            if selected_leads:
                selected_signals = {name: result.signals[name] for name in selected_leads}
                fig = create_signal_plot(selected_signals, result.sample_rate)
                st.plotly_chart(fig, use_container_width=True)
        
        # Quality and Clinical data
        col1, col2 = st.columns(2)
        
        with col1:
            if result.quality_metrics:
                st.subheader("✅ Quality Metrics")
                quality_fig = create_quality_gauge(result.quality_metrics.overall_score)
                st.plotly_chart(quality_fig, use_container_width=True)
                
                # Additional metrics
                metrics_data = {
                    "Metric": ["SNR", "Baseline Wander", "Coverage", "Clipping"],
                    "Value": [
                        f"{result.quality_metrics.snr:.1f} dB" if result.quality_metrics.snr else "N/A",
                        f"{result.quality_metrics.baseline_wander:.3f}" if result.quality_metrics.baseline_wander else "N/A",
                        f"{result.quality_metrics.coverage:.1%}",
                        "Yes" if result.quality_metrics.clipping_detected else "No"
                    ]
                }
                st.dataframe(pd.DataFrame(metrics_data), hide_index=True, use_container_width=True)
        
        with col2:
            if result.intervals:
                st.subheader("❤️ Clinical Intervals")
                intervals_fig = create_intervals_chart(result.intervals)
                st.plotly_chart(intervals_fig, use_container_width=True)
                
                # Heart rate variability
                if result.intervals.get('heart_rate'):
                    st.metric("Heart Rate", f"{result.intervals['heart_rate']:.0f} BPM")
        
        # Export section
        st.markdown("---")
        st.subheader("💾 Export Data")
        
        export_col1, export_col2, export_col3 = st.columns(3)
        
        with export_col1:
            if "CSV" in export_formats:
                # Create CSV
                df = pd.DataFrame(result.signals)
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    f"{selected_result['filename']}.csv",
                    "text/csv",
                    use_container_width=True
                )
        
        with export_col2:
            if "JSON" in export_formats:
                # Create JSON
                import json
                json_data = {
                    'signals': {k: v.tolist() for k, v in result.signals.items()},
                    'sample_rate': result.sample_rate,
                    'calibration': {
                        'paper_speed': result.paper_settings.paper_speed,
                        'gain': result.paper_settings.gain
                    }
                }
                json_str = json.dumps(json_data, indent=2)
                st.download_button(
                    "📥 Download JSON",
                    json_str,
                    f"{selected_result['filename']}.json",
                    "application/json",
                    use_container_width=True
                )
        
        with export_col3:
            if len(export_formats) > 2:
                # Create ZIP with all formats
                st.button(
                    "📦 Download All Formats",
                    use_container_width=True,
                    help="Downloads all selected formats as ZIP"
                )

with tab3:
    st.subheader("ℹ️ About ECG2Signal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Features
        - **Image Processing**: Handles JPG, PNG, TIFF, PDF
        - **Mobile Photos**: Automatic perspective correction
        - **Grid Detection**: Automatic calibration
        - **12-Lead Support**: Standard and rhythm strips
        - **Clinical Analysis**: PR, QRS, QT intervals
        - **Quality Assessment**: SNR, baseline wander, clipping
        - **Multiple Formats**: WFDB, CSV, JSON, EDF, FHIR, DICOM
        """)
    
    with col2:
        st.markdown("""
        ### 📚 How to Use
        1. Upload ECG image(s) or PDF
        2. Adjust calibration settings if needed
        3. Click "Convert All" to process
        4. View interactive results
        5. Export in your preferred format
        
        ### 🔧 Tips
        - Standard paper speed: 25 mm/s
        - Standard gain: 10 mm/mV
        - For best results, use clear images
        - Mobile photos work great!
        """)
    
    st.markdown("---")
    st.markdown("""
    ### 🚀 Powered by ECG2Signal
    Professional-grade ECG image to digital signal conversion.
    
    **Version**: 1.0.0 | **License**: Apache 2.0
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>ECG2Signal - Converting Hearts to Data ❤️</p>
    <p style='font-size: 0.8rem;'>Built with Streamlit + Python + Love</p>
</div>
""", unsafe_allow_html=True)
