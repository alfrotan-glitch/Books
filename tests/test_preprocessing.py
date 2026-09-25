"""
Unit tests for Computer Vision Preprocessing and Image Quality.
"""

import cv2
import numpy as np
import pytest

from src.preprocessing.cv_pipeline import ImagePreprocessor
from src.preprocessing.quality import ImageQualityAssessor


def test_image_quality_assessor():
    sharp_img = np.zeros((300, 300), dtype=np.uint8)
    sharp_img[100:200, 100:200] = 255
    metrics = ImageQualityAssessor.assess_quality(sharp_img)
    assert metrics["sharpness_score"] > 0
    assert metrics["contrast_score"] > 0
    assert 0.0 <= metrics["overall_quality_score"] <= 1.0


def test_deskew_detection():
    prep = ImagePreprocessor()
    img = np.ones((800, 600), dtype=np.uint8) * 255
    for y in range(150, 650, 40):
        cv2.line(img, (100, y), (500, y), 0, 2)

    center = (300, 400)
    rot_mat = cv2.getRotationMatrix2D(center, 3.5, 1.0)
    skewed = cv2.warpAffine(img, rot_mat, (600, 800), borderValue=255)

    detected_angle = prep.detect_deskew_angle(skewed)
    assert abs(detected_angle - (-3.5)) < 0.6


def test_shadow_removal_normalization():
    prep = ImagePreprocessor()
    img = np.ones((400, 400), dtype=np.uint8) * 255
    cv2.putText(img, "Shadow Test", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.0, 0, 2)

    # Add dark shadow to top-left corner
    shadow = np.zeros((400, 400), dtype=np.float32)
    for r in range(400):
        for c in range(400):
            shadow[r, c] = max(0.4, min(1.0, (r + c) / 500.0))

    shadowed = (img.astype(np.float32) * shadow).astype(np.uint8)
    normalized = prep.remove_shadows_and_normalize(shadowed)

    # Mean brightness of normalized background should be higher than shadowed
    assert normalized.mean() >= shadowed.mean()
