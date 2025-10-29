"""
Image denoising and enhancement for ECG images.
"""

import cv2
import numpy as np
from loguru import logger
from scipy.ndimage import median_filter


def denoise_image(image: np.ndarray, method: str = "bilateral") -> np.ndarray:
    """
    Denoise ECG image while preserving edges.

    Args:
        image: Input image
        method: Denoising method ('bilateral', 'nlmeans', 'gaussian', 'median')

    Returns:
        Denoised image
    """
    if method == "bilateral":
        return bilateral_denoise(image)
    elif method == "nlmeans":
        return nlmeans_denoise(image)
    elif method == "gaussian":
        return gaussian_denoise(image)
    elif method == "median":
        return median_denoise(image)
    else:
        logger.warning(f"Unknown method '{method}', using bilateral")
        return bilateral_denoise(image)


def bilateral_denoise(image: np.ndarray, d: int = 9, sigma_color: int = 75, sigma_space: int = 75) -> np.ndarray:
    """
    Apply bilateral filter (edge-preserving smoothing).

    Args:
        image: Input image
        d: Diameter of pixel neighborhood
        sigma_color: Filter sigma in color space
        sigma_space: Filter sigma in coordinate space

    Returns:
        Denoised image
    """
    if len(image.shape) == 3:
        result = cv2.bilateralFilter(image, d, sigma_color, sigma_space)
    else:
        result = cv2.bilateralFilter(image, d, sigma_color, sigma_space)

    return result


def nlmeans_denoise(image: np.ndarray, h: int = 10, template_window_size: int = 7, search_window_size: int = 21) -> np.ndarray:
    """
    Apply non-local means denoising.

    Args:
        image: Input image
        h: Filter strength
        template_window_size: Size of template patch
        search_window_size: Size of search area

    Returns:
        Denoised image
    """
    if len(image.shape) == 3:
        result = cv2.fastNlMeansDenoisingColored(image, None, h, h, template_window_size, search_window_size)
    else:
        result = cv2.fastNlMeansDenoising(image, None, h, template_window_size, search_window_size)

    return result


def gaussian_denoise(image: np.ndarray, kernel_size: int = 5, sigma: float = 1.0) -> np.ndarray:
    """
    Apply Gaussian blur for denoising.

    Args:
        image: Input image
        kernel_size: Kernel size (odd number)
        sigma: Standard deviation

    Returns:
        Denoised image
    """
    result = cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)
    return result


def median_denoise(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """
    Apply median filter for denoising.

    Args:
        image: Input image
        kernel_size: Kernel size

    Returns:
        Denoised image
    """
    if len(image.shape) == 3:
        result = np.zeros_like(image)
        for c in range(3):
            result[:, :, c] = cv2.medianBlur(image[:, :, c], kernel_size)
    else:
        result = cv2.medianBlur(image, kernel_size)

    return result


def enhance_contrast(image: np.ndarray, method: str = "clahe") -> np.ndarray:
    """
    Enhance image contrast.

    Args:
        image: Input image
        method: Enhancement method ('clahe', 'histogram', 'adaptive')

    Returns:
        Contrast-enhanced image
    """
    if method == "clahe":
        return apply_clahe(image)
    elif method == "histogram":
        return histogram_equalization(image)
    elif method == "adaptive":
        return adaptive_histogram_equalization(image)
    else:
        return apply_clahe(image)


def apply_clahe(image: np.ndarray, clip_limit: float = 2.0, tile_grid_size: tuple[int, int] = (8, 8)) -> np.ndarray:
    """
    Apply CLAHE (Contrast Limited Adaptive Histogram Equalization).

    Args:
        image: Input image
        clip_limit: Threshold for contrast limiting
        tile_grid_size: Size of grid for histogram equalization

    Returns:
        Enhanced image
    """
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

    if len(image.shape) == 3:
        # Convert to LAB and apply to L channel
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    else:
        result = clahe.apply(image)

    return result


def histogram_equalization(image: np.ndarray) -> np.ndarray:
    """
    Apply histogram equalization.

    Args:
        image: Input image

    Returns:
        Enhanced image
    """
    if len(image.shape) == 3:
        # Convert to YCrCb and equalize Y channel
        ycrcb = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
        ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
        result = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB)
    else:
        result = cv2.equalizeHist(image)

    return result


def adaptive_histogram_equalization(image: np.ndarray) -> np.ndarray:
    """
    Apply adaptive histogram equalization.

    Args:
        image: Input image

    Returns:
        Enhanced image
    """
    # Similar to CLAHE but with different parameters
    return apply_clahe(image, clip_limit=3.0, tile_grid_size=(16, 16))


def correct_illumination(image: np.ndarray) -> np.ndarray:
    """
    Correct non-uniform illumination.

    Args:
        image: Input image

    Returns:
        Illumination-corrected image
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image.copy()

    # Estimate background using morphological opening with large kernel
    kernel_size = max(gray.shape) // 20
    if kernel_size % 2 == 0:
        kernel_size += 1

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    background = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)

    # Blur background
    background = cv2.GaussianBlur(background, (kernel_size, kernel_size), 0)

    # Divide original by background
    corrected_gray = cv2.divide(gray, background, scale=255)

    if len(image.shape) == 3:
        # Apply correction to all channels
        result = image.copy().astype(np.float32)
        for c in range(3):
            result[:, :, c] = cv2.divide(image[:, :, c].astype(np.float32), background.astype(np.float32), scale=255)
        result = np.clip(result, 0, 255).astype(np.uint8)
    else:
        result = corrected_gray

    return result


def sharpen_image(image: np.ndarray, amount: float = 1.0) -> np.ndarray:
    """
    Sharpen image to enhance fine details.

    Args:
        image: Input image
        amount: Sharpening amount (0-2)

    Returns:
        Sharpened image
    """
    # Create sharpening kernel
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]) * amount / 9.0

    if len(image.shape) == 3:
        result = cv2.filter2D(image, -1, kernel)
    else:
        result = cv2.filter2D(image, -1, kernel)

    return np.clip(result, 0, 255).astype(image.dtype)


def remove_shadow(image: np.ndarray) -> np.ndarray:
    """
    Remove shadows from image.

    Args:
        image: Input image

    Returns:
        Shadow-removed image
    """
    if len(image.shape) == 3:
        # Convert to LAB
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l_channel = lab[:, :, 0]

        # Dilate L channel to estimate shadow
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        shadow_estimate = cv2.dilate(l_channel, kernel)
        shadow_estimate = cv2.medianBlur(shadow_estimate, 21)

        # Normalize
        l_corrected = (l_channel.astype(np.float32) / (shadow_estimate.astype(np.float32) + 1e-6) * 128).astype(np.uint8)
        lab[:, :, 0] = np.clip(l_corrected, 0, 255)

        result = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    else:
        # Similar process for grayscale
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        shadow_estimate = cv2.dilate(image, kernel)
        shadow_estimate = cv2.medianBlur(shadow_estimate, 21)

        result = (image.astype(np.float32) / (shadow_estimate.astype(np.float32) + 1e-6) * 128).astype(np.uint8)
        result = np.clip(result, 0, 255)

    return result
