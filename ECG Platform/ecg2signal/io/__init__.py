"""I/O module for loading and exporting ECG data in various formats."""

from ecg2signal.io.image_io import load_image, save_image
from ecg2signal.io.pdf import extract_pdf_pages
from ecg2signal.io.wfdb_io import write_wfdb, read_wfdb
from ecg2signal.io.edf_io import write_edf
from ecg2signal.io.fhir import write_fhir_observation
from ecg2signal.io.dcm_waveform import write_dicom_waveform

# Aliases for backward compatibility
export_wfdb = write_wfdb
load_wfdb = read_wfdb
export_edf = write_edf
export_fhir = write_fhir_observation
export_dicom_waveform = write_dicom_waveform

__all__ = [
    "load_image",
    "save_image",
    "extract_pdf_pages",
    "write_wfdb",
    "read_wfdb",
    "write_edf",
    "write_fhir_observation",
    "write_dicom_waveform",
    # Aliases
    "export_wfdb",
    "load_wfdb",
    "export_edf",
    "export_fhir",
    "export_dicom_waveform",
]
