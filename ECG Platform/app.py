
"""Streamlit UI for ECG2Signal."""
import streamlit as st
from pathlib import Path
import tempfile
from ecg2signal import ECGConverter
from ecg2signal.config import get_settings
from ecg2signal.utils.viz import plot_ecg_signals

st.set_page_config(page_title="ECG2Signal", page_icon="🫀", layout="wide")

st.title("🫀 ECG2Signal")
st.markdown("Convert ECG images to digital signals")

@st.cache_resource
def get_converter():
    return ECGConverter(get_settings())

uploaded_file = st.file_uploader("Upload ECG image or PDF", type=["jpg", "jpeg", "png", "pdf"])

col1, col2 = st.columns(2)
with col1:
    paper_speed = st.number_input("Paper Speed (mm/s)", value=25.0, min_value=10.0, max_value=50.0)
with col2:
    gain = st.number_input("Gain (mm/mV)", value=10.0, min_value=5.0, max_value=20.0)

if uploaded_file and st.button("Convert"):
    with st.spinner("Processing..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        
        try:
            converter = get_converter()
            result = converter.convert(tmp_path, paper_speed=paper_speed, gain=gain)
            
            st.success("✓ Conversion complete!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Quality Score", f"{result.quality_metrics.overall_score:.2f}")
            with col2:
                st.metric("Heart Rate", f"{result.intervals.heart_rate:.0f} BPM" if result.intervals.heart_rate else "N/A")
            with col3:
                st.metric("Duration", f"{result.duration_seconds:.1f} s")
            
            st.subheader("Signals")
            for lead_name in list(result.signals.keys())[:3]:
                with st.expander(f"Lead {lead_name}"):
                    st.line_chart(result.signals[lead_name])
            
            st.subheader("Export")
            output_dir = Path(tempfile.mkdtemp())
            result.export_json(str(output_dir / "ecg.json"))
            
            with open(output_dir / "ecg.json", "rb") as f:
                st.download_button("Download JSON", f, file_name="ecg.json")
        
        finally:
            Path(tmp_path).unlink(missing_ok=True)
