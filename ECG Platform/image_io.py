"""
Image I/O operations for ECG images.
"""

from pathlib import Path

import cv2
import numpy as np
from loguru import logger
from PIL import Image


def load_image(image_path: str, grayscale: bool = False) -> np.ndarray:
    """
    Load an image from file.

    Args:
        image_path: Path to image file
        grayscale: If True, convert to grayscale

    Returns:
        Image as numpy array (RGB or grayscale)

    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If image cannot be loaded
    """
    img_file = Path(image_path)
    if not img_file.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    suffix = img_file.suffix.lower()
    supported = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp"}

    if suffix not in supported:
        raise ValueError(f"Unsupported image format: {suffix}")

    try:
        # Use OpenCV for loading
        if grayscale:
            img = cv2.imread(str(img_file), cv2.IMREAD_GRAYSCALE)
        else:
            img = cv2.imread(str(img_file), cv2.IMREAD_COLOR)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")

        logger.info(f"Loaded image: {img.shape}, dtype={img.dtype}")
        return img

    except Exception as e:
        logger.error(f"Error loading image {image_path}: {e}")
        raise


def save_image(image: np.ndarray, output_path: str, quality: int = 95) -> None:
    """
    Save an image to file.

    Args:
        image: Image array to save
        output_path: Output file path
        quality: JPEG quality (1-100)
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Convert RGB to BGR for OpenCV
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Save with appropriate parameters
    suffix = out_file.suffix.lower()
    if suffix in [".jpg", ".jpeg"]:
        cv2.imwrite(str(out_file), image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    elif suffix == ".png":
        cv2.imwrite(str(out_file), image, [cv2.IMWRITE_PNG_COMPRESSION, 3])
    else:
        cv2.imwrite(str(out_file), image)

    logger.info(f"Saved image to: {output_path}")


def load_image_pil(image_path: str) -> Image.Image:
    """
    Load image using PIL (useful for handling special formats).

    Args:
        image_path: Path to image file

    Returns:
        PIL Image object
    """
    img_file = Path(image_path)
    if not img_file.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    try:
        pil_img = Image.open(img_file)
        logger.info(f"Loaded PIL image: size={pil_img.size}, mode={pil_img.mode}")
        return pil_img
    except Exception as e:
        logger.error(f"Error loading PIL image {image_path}: {e}")
        raise


def pil_to_numpy(pil_img: Image.Image) -> np.ndarray:
    """
    Convert PIL Image to numpy array.

    Args:
        pil_img: PIL Image object

    Returns:
        Numpy array (RGB)
    """
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")
    return np.array(pil_img)


def numpy_to_pil(img_array: np.ndarray) -> Image.Image:
    """
    Convert numpy array to PIL Image.

    Args:
        img_array: Numpy array (RGB or grayscale)

    Returns:
        PIL Image object
    """
    if img_array.dtype == np.float32 or img_array.dtype == np.float64:
        img_array = (img_array * 255).astype(np.uint8)
    return Image.fromarray(img_array)


def resize_image(
    image: np.ndarray,
    target_size: tuple[int, int] | None = None,
    max_size: int | None = None,
    interpolation: int = cv2.INTER_LINEAR,
) -> np.ndarray:
    """
    Resize image to target size or max dimension.

    Args:
        image: Input image
        target_size: Target (width, height), or None
        max_size: Maximum dimension size, or None
        interpolation: OpenCV interpolation method

    Returns:
        Resized image
    """
    h, w = image.shape[:2]

    if target_size is not None:
        return cv2.resize(image, target_size, interpolation=interpolation)

    if max_size is not None:
        scale = max_size / max(h, w)
        if scale < 1.0:
            new_w = int(w * scale)
            new_h = int(h * scale)
            return cv2.resize(image, (new_w, new_h), interpolation=interpolation)

    return image


def normalize_image(image: np.ndarray) -> np.ndarray:
    """
    Normalize image to [0, 1] float range.

    Args:
        image: Input image

    Returns:
        Normalized image
    """
    if image.dtype == np.uint8:
        return image.astype(np.float32) / 255.0
    elif image.dtype == np.uint16:
        return image.astype(np.float32) / 65535.0
    return image.astype(np.float32)


def to_uint8(image: np.ndarray) -> np.ndarray:
    """
    Convert image to uint8 format.

    Args:
        image: Input image (any dtype)

    Returns:
        uint8 image
    """
    if image.dtype == np.uint8:
        return image

    if image.max() <= 1.0:
        return (image * 255).astype(np.uint8)

    return np.clip(image, 0, 255).astype(np.uint8)
