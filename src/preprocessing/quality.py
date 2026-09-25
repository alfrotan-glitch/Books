"""
Image Quality Assessment Engine.
Computes blur, contrast, brightness uniformity, and noise metrics for document images.
"""

from typing import Dict, Tuple
import cv2
import numpy as np


class ImageQualityAssessor:
    @staticmethod
    def assess_quality(image: np.ndarray) -> Dict[str, float]:
        """
        Assess quality metrics of a document image.
        Returns sharpness, contrast, brightness, noise, and overall score (0.0 to 1.0).
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY if image.shape[2] == 3 else cv2.COLOR_RGB2GRAY)
        else:
            gray = image

        # 1. Sharpness via Laplacian Variance
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        lap_var = float(laplacian.var())
        # Map variance to 0..1 score (var >= 300 is sharp document, < 60 is blurry)
        sharpness_score = min(1.0, max(0.0, lap_var / 350.0))

        # 2. Contrast via Standard Deviation of Pixel Intensities
        contrast_std = float(gray.std())
        # Document images typically have high contrast (bimodal, std >= 50)
        contrast_score = min(1.0, max(0.0, contrast_std / 70.0))

        # 3. Brightness & Uniformity
        mean_brightness = float(gray.mean())
        # Ideal page brightness is 180-240 (white paper)
        if mean_brightness > 120 and mean_brightness < 250:
            brightness_score = 1.0 - abs(mean_brightness - 220) / 120.0
        else:
            brightness_score = 0.4
        brightness_score = min(1.0, max(0.1, brightness_score))

        # 4. Illumination Uniformity (check quadrant brightness differences)
        h, w = gray.shape
        q1 = gray[0 : h // 2, 0 : w // 2].mean()
        q2 = gray[0 : h // 2, w // 2 : w].mean()
        q3 = gray[h // 2 : h, 0 : w // 2].mean()
        q4 = gray[h // 2 : h, w // 2 : w].mean()
        max_diff = max(abs(q1 - q2), abs(q1 - q3), abs(q1 - q4), abs(q2 - q4), abs(q3 - q4))
        uniformity_score = max(0.0, 1.0 - (max_diff / 80.0))

        # 5. Noise estimation via difference from median blur
        blurred = cv2.medianBlur(gray, 3)
        noise_diff = np.mean(np.abs(gray.astype(np.float32) - blurred.astype(np.float32)))
        noise_score = max(0.0, 1.0 - (noise_diff / 15.0))

        # Weighted aggregate score
        overall_score = (
            0.35 * sharpness_score
            + 0.25 * contrast_score
            + 0.15 * brightness_score
            + 0.15 * uniformity_score
            + 0.10 * noise_score
        )

        return {
            "laplacian_variance": round(lap_var, 2),
            "sharpness_score": round(sharpness_score, 3),
            "contrast_std": round(contrast_std, 2),
            "contrast_score": round(contrast_score, 3),
            "mean_brightness": round(mean_brightness, 2),
            "uniformity_score": round(uniformity_score, 3),
            "noise_score": round(noise_score, 3),
            "overall_quality_score": round(overall_score, 3),
        }
