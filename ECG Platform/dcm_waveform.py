"""
DICOM Waveform (SCP-ECG) format writer for ECG signals.
"""

from datetime import datetime
from pathlib import Path

import numpy as np
import pydicom
from loguru import logger
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid


def write_dicom_waveform(ecg_result, output_path: str) -> None:
    """
    Write ECG signals to DICOM Waveform format.

    Args:
        ecg_result: ECGResult object
        output_path: Output DICOM file path (.dcm)
    """
    from ecg2signal.types import ECGResult

    if not isinstance(ecg_result, ECGResult):
        raise TypeError("ecg_result must be ECGResult instance")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Create file dataset
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.9.1.1"  # 12-Lead ECG Waveform
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
    file_meta.ImplementationClassUID = generate_uid()
    file_meta.ImplementationVersionName = "ECG2SIGNAL_1_0"

    ds = FileDataset(
        str(output_file),
        {},
        file_meta=file_meta,
        preamble=b"\0" * 128,
    )

    # Patient module
    ds.PatientName = ecg_result.metadata.patient_name or "UNKNOWN"
    ds.PatientID = ecg_result.metadata.patient_id or "000000"
    ds.PatientBirthDate = ""
    ds.PatientSex = (ecg_result.metadata.gender or "O")[0].upper()

    # General Study module
    ds.StudyInstanceUID = generate_uid()
    ds.StudyDate = datetime.now().strftime("%Y%m%d")
    ds.StudyTime = datetime.now().strftime("%H%M%S")
    ds.ReferringPhysicianName = ""
    ds.StudyID = "1"
    ds.AccessionNumber = ""

    # General Series module
    ds.SeriesInstanceUID = generate_uid()
    ds.SeriesNumber = 1
    ds.Modality = "ECG"

    # General Equipment module
    ds.Manufacturer = "ECG2Signal"
    ds.ManufacturerModelName = "ECG2Signal v1.0"
    ds.SoftwareVersions = "1.0"

    # General Image module
    ds.InstanceNumber = 1
    ds.ContentDate = datetime.now().strftime("%Y%m%d")
    ds.ContentTime = datetime.now().strftime("%H%M%S")

    # SOP Common module
    ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID

    # Waveform Identification module
    ds.InstanceCreationDate = datetime.now().strftime("%Y%m%d")
    ds.InstanceCreationTime = datetime.now().strftime("%H%M%S")

    # Waveform module
    waveform_seq = []

    # Prepare multiplexed waveform data
    signal_names = sorted(ecg_result.signals.keys())
    n_channels = len(signal_names)
    n_samples = ecg_result.num_samples

    # Create waveform sequence item
    waveform_item = Dataset()

    # Multiplex group
    waveform_item.MultiplexGroupLabel = "ECG"
    waveform_item.MultiplexGroupUID = generate_uid()
    waveform_item.MultiplexGroupTimeOffset = 0.0
    waveform_item.TriggerTimeOffset = 0.0

    # Waveform sample interpretation
    waveform_item.WaveformOriginality = "ORIGINAL"
    waveform_item.NumberOfWaveformChannels = n_channels
    waveform_item.NumberOfWaveformSamples = n_samples
    waveform_item.SamplingFrequency = float(ecg_result.sample_rate)

    # Channel definition sequence
    channel_seq = []
    for i, lead_name in enumerate(signal_names):
        channel_item = Dataset()

        # Channel source
        channel_source = Dataset()
        channel_source.CodeValue = _get_snomed_code(lead_name)
        channel_source.CodingSchemeDesignator = "SCT"  # SNOMED CT
        channel_source.CodeMeaning = f"Lead {lead_name}"

        channel_item.ChannelSourceSequence = [channel_source]

        # Channel sensitivity and units
        channel_item.ChannelSensitivity = 1.0  # 1 unit = 1 mV
        channel_item.ChannelSensitivityUnitsSequence = [_create_unit_sequence("mV")]
        channel_item.ChannelSensitivityCorrectionFactor = 1.0
        channel_item.ChannelBaseline = 0.0

        # Channel properties
        channel_item.WaveformBitsStored = 16
        channel_item.ChannelSampleSkew = 0.0
        channel_item.ChannelOffset = 0.0

        # Filter settings
        channel_item.FilterLowFrequency = 0.05
        channel_item.FilterHighFrequency = 150.0

        channel_seq.append(channel_item)

    waveform_item.ChannelDefinitionSequence = channel_seq

    # Prepare waveform data (interleaved)
    waveform_data = np.zeros((n_samples * n_channels,), dtype=np.int16)
    for i, lead_name in enumerate(signal_names):
        signal = ecg_result.signals[lead_name]
        # Scale to int16 (±32767 represents ±32.767 mV)
        signal_scaled = np.clip(signal * 1000, -32767, 32767).astype(np.int16)
        waveform_data[i::n_channels] = signal_scaled

    waveform_item.WaveformData = waveform_data.tobytes()

    waveform_seq.append(waveform_item)
    ds.WaveformSequence = waveform_seq

    # Acquisition Context module
    ds.AcquisitionDateTime = datetime.now().strftime("%Y%m%d%H%M%S")

    # Save DICOM file
    try:
        ds.save_as(str(output_file), write_like_original=False)
        logger.info(f"Wrote DICOM Waveform: {output_path}")

    except Exception as e:
        logger.error(f"Failed to write DICOM Waveform: {e}")
        raise


def _get_snomed_code(lead_name: str) -> str:
    """
    Get SNOMED CT code for ECG lead.

    Args:
        lead_name: Lead name

    Returns:
        SNOMED CT code
    """
    snomed_map = {
        "I": "251200008",
        "II": "251201007",
        "III": "251202000",
        "aVR": "251203005",
        "AVR": "251203005",
        "aVL": "251204004",
        "AVL": "251204004",
        "aVF": "251205003",
        "AVF": "251205003",
        "V1": "251206002",
        "V2": "251207006",
        "V3": "251208001",
        "V4": "251209009",
        "V5": "251210004",
        "V6": "251211000",
    }

    return snomed_map.get(lead_name.upper(), "251146004")  # Generic ECG lead


def _create_unit_sequence(unit: str) -> Dataset:
    """
    Create unit sequence dataset for DICOM.

    Args:
        unit: Unit string (e.g., 'mV', 'uV')

    Returns:
        Dataset with unit coding
    """
    unit_item = Dataset()
    unit_item.CodeValue = "mV" if unit == "mV" else "uV"
    unit_item.CodingSchemeDesignator = "UCUM"
    unit_item.CodeMeaning = "millivolt" if unit == "mV" else "microvolt"
    return unit_item


def read_dicom_waveform(dcm_path: str) -> tuple[dict, dict]:
    """
    Read DICOM Waveform file.

    Args:
        dcm_path: Path to DICOM file

    Returns:
        Tuple of (signals dict, metadata dict)
    """
    try:
        ds = pydicom.dcmread(dcm_path)

        # Extract waveform data
        signals = {}
        metadata = {}

        if hasattr(ds, "WaveformSequence"):
            waveform = ds.WaveformSequence[0]

            n_channels = waveform.NumberOfWaveformChannels
            n_samples = waveform.NumberOfWaveformSamples
            sample_rate = float(waveform.SamplingFrequency)

            # Read waveform data
            waveform_data = np.frombuffer(waveform.WaveformData, dtype=np.int16)
            waveform_data = waveform_data.reshape((n_samples, n_channels))

            # Extract channel names and convert to mV
            for i, channel in enumerate(waveform.ChannelDefinitionSequence):
                lead_name = channel.ChannelSourceSequence[0].CodeMeaning.replace("Lead ", "")
                signal = waveform_data[:, i].astype(np.float32) / 1000.0  # Convert to mV
                signals[lead_name] = signal

            metadata = {
                "sample_rate": sample_rate,
                "n_channels": n_channels,
                "n_samples": n_samples,
                "patient_name": str(ds.PatientName) if hasattr(ds, "PatientName") else None,
                "patient_id": ds.PatientID if hasattr(ds, "PatientID") else None,
                "acquisition_datetime": ds.AcquisitionDateTime
                if hasattr(ds, "AcquisitionDateTime")
                else None,
            }

        logger.info(f"Read DICOM Waveform: {dcm_path}")
        return signals, metadata

    except Exception as e:
        logger.error(f"Failed to read DICOM Waveform: {e}")
        raise


def validate_dicom_waveform(dcm_path: str) -> bool:
    """
    Validate DICOM Waveform file.

    Args:
        dcm_path: Path to DICOM file

    Returns:
        True if valid, False otherwise
    """
    try:
        ds = pydicom.dcmread(dcm_path)
        return hasattr(ds, "WaveformSequence") and len(ds.WaveformSequence) > 0
    except Exception:
        return False
