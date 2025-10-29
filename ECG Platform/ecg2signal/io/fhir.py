"""
HL7 FHIR Observation resource encoder for ECG data.
"""

import json
from datetime import datetime
from pathlib import Path

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.observation import Observation, ObservationComponent
from fhir.resources.quantity import Quantity
from fhir.resources.reference import Reference
from fhir.resources.sampleddata import SampledData
from loguru import logger


def write_fhir_observation(ecg_result, patient_id: str, output_path: str) -> None:
    """
    Write ECG data as HL7 FHIR Observation resource.

    Args:
        ecg_result: ECGResult object
        patient_id: Patient identifier
        output_path: Output JSON file path
    """
    from ecg2signal.types import ECGResult

    if not isinstance(ecg_result, ECGResult):
        raise TypeError("ecg_result must be ECGResult instance")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Create FHIR Observation
    observation = Observation(
        resourceType="Observation",
        status="final",
        category=[
            CodeableConcept(
                coding=[
                    Coding(
                        system="http://terminology.hl7.org/CodeSystem/observation-category",
                        code="procedure",
                        display="Procedure",
                    )
                ]
            )
        ],
        code=CodeableConcept(
            coding=[
                Coding(
                    system="http://loinc.org",
                    code="11524-6",
                    display="EKG study",
                )
            ]
        ),
        subject=Reference(reference=f"Patient/{patient_id}"),
        effectiveDateTime=datetime.now().isoformat(),
        issued=datetime.now().isoformat(),
    )

    # Add components for each lead
    components = []
    for lead_name, signal in ecg_result.signals.items():
        # Create SampledData for waveform
        sampled_data = SampledData(
            origin=Quantity(value=0.0, unit="mV", system="http://unitsofmeasure.org", code="mV"),
            period=1000.0 / ecg_result.sample_rate,  # Period in milliseconds
            dimensions=1,
            data=" ".join([f"{v:.6f}" for v in signal.tolist()]),
        )

        # Create component
        component = ObservationComponent(
            code=CodeableConcept(
                coding=[
                    Coding(
                        system="http://loinc.org",
                        code=_get_loinc_code(lead_name),
                        display=f"ECG Lead {lead_name}",
                    )
                ]
            ),
            valueSampledData=sampled_data,
        )

        components.append(component)

    observation.component = components

    # Add metadata as extensions or notes
    observation.note = [
        {
            "text": f"Paper speed: {ecg_result.paper_settings.paper_speed} mm/s, "
            f"Gain: {ecg_result.paper_settings.gain} mm/mV, "
            f"Quality score: {ecg_result.quality_metrics.overall_score:.3f}"
        }
    ]

    # Add interval measurements as additional components
    if ecg_result.intervals.heart_rate:
        hr_component = ObservationComponent(
            code=CodeableConcept(
                coding=[
                    Coding(
                        system="http://loinc.org",
                        code="8867-4",
                        display="Heart rate",
                    )
                ]
            ),
            valueQuantity=Quantity(
                value=ecg_result.intervals.heart_rate,
                unit="beats/minute",
                system="http://unitsofmeasure.org",
                code="/min",
            ),
        )
        components.append(hr_component)

    # Write to file
    try:
        fhir_json = observation.json(indent=2)
        with open(output_file, "w") as f:
            f.write(fhir_json)

        logger.info(f"Wrote FHIR Observation: {output_path}")

    except Exception as e:
        logger.error(f"Failed to write FHIR Observation: {e}")
        raise


def _get_loinc_code(lead_name: str) -> str:
    """
    Get LOINC code for ECG lead.

    Args:
        lead_name: Lead name (I, II, III, aVR, aVL, aVF, V1-V6)

    Returns:
        LOINC code string
    """
    loinc_map = {
        "I": "131329",
        "II": "131330",
        "III": "131331",
        "aVR": "131332",
        "AVR": "131332",
        "aVL": "131333",
        "AVL": "131333",
        "aVF": "131334",
        "AVF": "131334",
        "V1": "131335",
        "V2": "131336",
        "V3": "131337",
        "V4": "131338",
        "V5": "131339",
        "V6": "131340",
    }

    return loinc_map.get(lead_name.upper(), "11524-6")  # Default to generic ECG code


def read_fhir_observation(fhir_path: str) -> dict:
    """
    Read FHIR Observation from JSON file.

    Args:
        fhir_path: Path to FHIR JSON file

    Returns:
        Dictionary with parsed FHIR data
    """
    try:
        observation = Observation.parse_file(fhir_path)

        # Extract signals from components
        signals = {}
        for component in observation.component or []:
            if component.valueSampledData:
                lead_name = component.code.coding[0].display.replace("ECG Lead ", "")
                data_str = component.valueSampledData.data
                signal = [float(v) for v in data_str.split()]
                signals[lead_name] = signal

        metadata = {
            "patient_id": observation.subject.reference.split("/")[-1],
            "datetime": observation.effectiveDateTime,
            "status": observation.status,
            "signals": signals,
        }

        logger.info(f"Read FHIR Observation: {fhir_path}")
        return metadata

    except Exception as e:
        logger.error(f"Failed to read FHIR Observation: {e}")
        raise


def validate_fhir_observation(fhir_path: str) -> bool:
    """
    Validate FHIR Observation file.

    Args:
        fhir_path: Path to FHIR JSON file

    Returns:
        True if valid, False otherwise
    """
    try:
        observation = Observation.parse_file(fhir_path)
        return observation.status is not None and observation.code is not None
    except Exception:
        return False
