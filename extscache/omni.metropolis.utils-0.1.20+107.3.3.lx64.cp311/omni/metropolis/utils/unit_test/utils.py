import numpy as np


def compare_images_diff_percent(target_image: np.ndarray, golden_image: np.ndarray) -> float:
    """compare the image distance of two image stored in np array format"""
    assert (
        target_image.shape == golden_image.shape
    ), f"Shape mismatch: target {target_image.shape}, golden {golden_image.shape}"

    diff = np.abs(target_image.astype(np.int32) - golden_image.astype(np.int32))
    diff_pixels = np.any(diff > 0, axis=-1)
    diff_count = np.sum(diff_pixels)
    total_pixels = target_image.shape[0] * target_image.shape[1]

    diff_percent = float(diff_count) / float(total_pixels)
    return diff_percent
