"""
Computer Vision Preprocessing Pipeline for Scanned Books and Mobile/CamScanner Captures.
Performs deskew, rotation detection, shadow removal, border cleanup, and contrast normalization.
Preserves original image and provides full traceability.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import cv2
import numpy as np

from src.config import ExtractionConfig, default_config
from src.preprocessing.quality import ImageQualityAssessor


@dataclass
class PreprocessingResult:
    original_image: np.ndarray
    processed_image: np.ndarray
    deskew_angle: float = 0.0
    rotation_angle: int = 0
    border_removed: bool = False
    shadow_removed: bool = False
    quality_metrics: Dict[str, float] = None


class ImagePreprocessor:
    def __init__(self, config: Optional[ExtractionConfig] = None):
        self.config = config or default_config

    def to_grayscale(self, image: np.ndarray) -> np.ndarray:
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        return image

    def remove_shadows_and_normalize(self, gray: np.ndarray) -> np.ndarray:
        """
        CamScanner shadow removal and background whitening.
        Estimates the background illumination plane using a large morphological close,
        then divides the image by the background to normalize lighting gradients.
        """
        # Downsample background estimation for performance on large images
        h, w = gray.shape
        scale = min(1.0, 800.0 / max(h, w))
        if scale < 1.0:
            small = cv2.resize(gray, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        else:
            small = gray

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
        bg_small = cv2.morphologyEx(small, cv2.MORPH_CLOSE, kernel)
        bg_small = cv2.GaussianBlur(bg_small, (21, 21), 0)

        if scale < 1.0:
            background = cv2.resize(bg_small, (w, h), interpolation=cv2.INTER_LINEAR)
        else:
            background = bg_small

        # Avoid zero division
        background = np.maximum(background, 1)

        normalized = np.clip((gray.astype(np.float32) / background.astype(np.float32)) * 255.0, 0, 255).astype(np.uint8)
        return normalized

    def detect_orthogonal_rotation(self, gray: np.ndarray) -> int:
        """
        Detects if a document is rotated by 90, 180, or 270 degrees.
        Uses morphological text line aspect ratio comparison (horizontal vs vertical lines).
        """
        h, w = gray.shape
        scale = min(1.0, 1000.0 / max(h, w))
        if scale < 1.0:
            small = cv2.resize(gray, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        else:
            small = gray

        _, thresh = cv2.threshold(small, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Compare horizontal text merging vs vertical text merging
        h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 2))
        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 20))

        h_dil = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, h_kernel)
        v_dil = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, v_kernel)

        h_contours, _ = cv2.findContours(h_dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        v_contours, _ = cv2.findContours(v_dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        h_lines = sum(
            1 for c in h_contours
            if cv2.boundingRect(c)[2] > cv2.boundingRect(c)[3] * 2.5 and cv2.boundingRect(c)[2] > 40
        )
        v_lines = sum(
            1 for c in v_contours
            if cv2.boundingRect(c)[3] > cv2.boundingRect(c)[2] * 2.5 and cv2.boundingRect(c)[3] > 40
        )

        # If vertical lines strongly dominate, document is rotated 90 degrees
        if v_lines >= 2 and v_lines > h_lines * 2.0:
            return 90
        return 0

    def detect_deskew_angle(self, gray: np.ndarray) -> float:
        """
        Calculates skew angle using projection profile variance across angles.
        Robust to varying text styles and fonts.
        """
        h, w = gray.shape
        scale = min(1.0, 1000.0 / max(h, w))
        if scale < 1.0:
            small = cv2.resize(gray, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        else:
            small = gray

        # Otsu thresholding inverted (text = white, background = black)
        _, thresh = cv2.threshold(small, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Morphological horizontal dilation to merge letters into line strips
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3))
        dilated = cv2.dilate(thresh, kernel, iterations=1)

        # Search angle in range [-12, +12] degrees in 0.5 deg steps
        best_angle = 0.0
        max_variance = -1.0

        angles = np.arange(-12.0, 12.5, 0.5)
        ch, cw = dilated.shape
        center = (cw // 2, ch // 2)

        for angle in angles:
            rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(dilated, rot_mat, (cw, ch), flags=cv2.INTER_NEAREST, borderValue=0)
            proj = np.sum(rotated, axis=1)
            variance = np.var(proj)
            if variance > max_variance:
                max_variance = variance
                best_angle = angle

        # Fine-tune in 0.1 deg steps around best_angle
        fine_angles = np.arange(best_angle - 0.4, best_angle + 0.5, 0.1)
        for angle in fine_angles:
            rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(dilated, rot_mat, (cw, ch), flags=cv2.INTER_NEAREST, borderValue=0)
            proj = np.sum(rotated, axis=1)
            variance = np.var(proj)
            if variance > max_variance:
                max_variance = variance
                best_angle = angle

        return float(best_angle)

    def rotate_image(self, image: np.ndarray, angle: float, border_value: int = 255) -> np.ndarray:
        """Rotates image by arbitrary angle, expanding borders to avoid cropping corners."""
        if abs(angle) < 0.1:
            return image

        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)

        # Calculate bounding box dimensions of rotated image
        cos = np.abs(rot_mat[0, 0])
        sin = np.abs(rot_mat[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))

        rot_mat[0, 2] += (new_w / 2) - center[0]
        rot_mat[1, 2] += (new_h / 2) - center[1]

        border_color = (border_value, border_value, border_value) if len(image.shape) == 3 else border_value
        return cv2.warpAffine(
            image, rot_mat, (new_w, new_h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=border_color
        )

    def remove_scan_borders(self, gray: np.ndarray, border_ratio: float = 0.04) -> np.ndarray:
        """
        Detects and removes black scanner border edges, dark binder marks, or scan bed edges.
        Fills dark border regions in outer margins with white (255).
        """
        result = gray.copy()
        h, w = gray.shape
        margin_y = int(h * border_ratio)
        margin_x = int(w * border_ratio)

        border_mask = np.zeros_like(gray, dtype=np.uint8)
        border_mask[0:margin_y, :] = 255
        border_mask[h - margin_y : h, :] = 255
        border_mask[:, 0:margin_x] = 255
        border_mask[:, w - margin_x : w] = 255

        dark_pixels = (gray < 85) & (border_mask == 255)
        result[dark_pixels] = 255
        return result

    def enhance_contrast_clahe(self, gray: np.ndarray) -> np.ndarray:
        """Contrast Limited Adaptive Histogram Equalization for crisp text extraction."""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(gray)

    def denoise_image(self, gray: np.ndarray) -> np.ndarray:
        """Gentle denoising that removes paper grain without softening text edges."""
        return cv2.fastNlMeansDenoising(gray, None, h=7, templateWindowSize=7, searchWindowSize=21)

    def adaptive_binarize(self, gray: np.ndarray) -> np.ndarray:
        """High-accuracy adaptive thresholding for clear OCR characters."""
        return cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 10
        )

    def preprocess_for_ocr(self, image: np.ndarray) -> PreprocessingResult:
        """
        Main non-destructive preprocessing pipeline for document images.
        Execution order:
        1. Grayscale conversion
        2. Shadow removal / illumination normalization (flattens gradients before geometric transforms)
        3. Orthogonal rotation check (90/180/270)
        4. Deskew check (-12 to +12 deg)
        5. Border cleanup
        6. Contrast enhancement (CLAHE) & gentle denoising
        """
        quality = ImageQualityAssessor.assess_quality(image)
        gray = self.to_grayscale(image)

        # 1. Shadow Removal / Illumination Normalization FIRST
        shadow_removed = False
        if self.config.enable_shadow_removal:
            gray = self.remove_shadows_and_normalize(gray)
            shadow_removed = True

        # 2. Rotation Check
        rotation_angle = 0
        if self.config.enable_auto_rotation:
            rotation_angle = self.detect_orthogonal_rotation(gray)
            if rotation_angle != 0:
                gray = np.rot90(gray, k=-rotation_angle // 90)

        # 3. Deskew Check
        deskew_angle = 0.0
        if self.config.enable_deskew:
            deskew_angle = self.detect_deskew_angle(gray)
            if abs(deskew_angle) > 0.2 and abs(deskew_angle) <= self.config.max_deskew_angle:
                gray = self.rotate_image(gray, -deskew_angle, border_value=255)

        # 4. Border Removal
        border_removed = False
        if self.config.enable_border_removal:
            gray = self.remove_scan_borders(gray)
            border_removed = True

        # 5. Contrast Enhancement
        if self.config.enable_clahe:
            gray = self.enhance_contrast_clahe(gray)

        # 6. Denoising
        if self.config.enable_denoising:
            gray = self.denoise_image(gray)

        processed_rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

        return PreprocessingResult(
            original_image=image,
            processed_image=processed_rgb,
            deskew_angle=deskew_angle,
            rotation_angle=rotation_angle,
            border_removed=border_removed,
            shadow_removed=shadow_removed,
            quality_metrics=quality,
        )
