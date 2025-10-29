"""
PDF processing for ECG images.
"""

from pathlib import Path

import numpy as np
from loguru import logger
from pdf2image import convert_from_path
from pypdf import PdfReader


def extract_pdf_pages(pdf_path: str, dpi: int = 300) -> list[np.ndarray]:
    """
    Extract pages from PDF as images.

    Args:
        pdf_path: Path to PDF file
        dpi: Resolution for image extraction

    Returns:
        List of page images as numpy arrays (RGB)
    """
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    logger.info(f"Extracting pages from PDF: {pdf_path}")

    try:
        # Convert PDF pages to images
        pil_images = convert_from_path(str(pdf_file), dpi=dpi)
        logger.info(f"Extracted {len(pil_images)} pages at {dpi} DPI")

        # Convert PIL images to numpy arrays
        images = []
        for i, pil_img in enumerate(pil_images):
            img_array = np.array(pil_img)
            images.append(img_array)
            logger.debug(f"Page {i+1}: shape={img_array.shape}, dtype={img_array.dtype}")

        return images

    except Exception as e:
        logger.error(f"Failed to extract PDF pages: {e}")
        raise


def get_pdf_metadata(pdf_path: str) -> dict:
    """
    Extract metadata from PDF file.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Dictionary with PDF metadata
    """
    try:
        reader = PdfReader(pdf_path)
        metadata = {
            "num_pages": len(reader.pages),
            "title": reader.metadata.get("/Title", ""),
            "author": reader.metadata.get("/Author", ""),
            "subject": reader.metadata.get("/Subject", ""),
            "creator": reader.metadata.get("/Creator", ""),
            "producer": reader.metadata.get("/Producer", ""),
            "creation_date": reader.metadata.get("/CreationDate", ""),
        }
        return metadata
    except Exception as e:
        logger.warning(f"Could not extract PDF metadata: {e}")
        return {}


def is_valid_pdf(pdf_path: str) -> bool:
    """
    Check if file is a valid PDF.

    Args:
        pdf_path: Path to PDF file

    Returns:
        True if valid PDF, False otherwise
    """
    try:
        reader = PdfReader(pdf_path)
        return len(reader.pages) > 0
    except Exception:
        return False
