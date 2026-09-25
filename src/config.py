"""
Configuration module for the PDF Book Text Extraction System.
Defines parameters for forensics, OCR, image preprocessing, layout analysis,
reading order, checkpointing, and output generation.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ExtractionConfig:
    # Directory paths
    workspace_root: Path = field(default_factory=lambda: Path.cwd())
    inbox_dir: Path = field(default_factory=lambda: Path.cwd() / "inbox")
    output_dir: Path = field(default_factory=lambda: Path.cwd() / "output")
    debug_dir: Path = field(default_factory=lambda: Path.cwd() / "debug")
    logs_dir: Path = field(default_factory=lambda: Path.cwd() / "logs")
    checkpoints_dir: Path = field(default_factory=lambda: Path.cwd() / "checkpoints")

    # Rendering & Resolution
    ocr_dpi: int = 300
    fast_dpi: int = 150

    # Forensics & Text Layer Thresholds
    min_native_chars: int = 40
    min_native_words: int = 8
    max_corrupt_char_ratio: float = 0.12  # control chars, CID unmapped, replacement chars
    min_printable_ratio: float = 0.85

    # Image Preprocessing Controls
    enable_deskew: bool = True
    max_deskew_angle: float = 25.0
    enable_auto_rotation: bool = True  # 90, 180, 270 deg
    enable_shadow_removal: bool = True
    enable_border_removal: bool = True
    enable_denoising: bool = True
    enable_clahe: bool = True
    enable_adaptive_binarization: bool = True
    save_debug_images: bool = False

    # OCR Engines
    # engine choices: "auto", "rapidocr", "tesseract", "hybrid"
    ocr_engine: str = "auto"
    tesseract_cmd: Optional[str] = None
    tesseract_languages: str = "fas+ara+eng"
    rapidocr_use_det: bool = True
    rapidocr_use_cls: bool = True
    rapidocr_use_rec: bool = True
    min_ocr_confidence: float = 0.45
    high_ocr_confidence: float = 0.78
    ocr_agreement_threshold: float = 0.80

    # Layout Analysis & Column Detection
    column_detection_mode: str = "auto"  # "auto", "single", "double", "multi"
    max_columns: int = 4
    min_column_gutter_ratio: float = 0.015  # min gutter width relative to page width
    header_margin_ratio: float = 0.08      # top 8% of page
    footer_margin_ratio: float = 0.08      # bottom 8% of page
    footnote_max_ratio_from_bottom: float = 0.28
    table_min_cells: int = 4

    # Reading Order
    reading_order_mode: str = "auto"  # "auto", "ltr", "rtl"
    detect_language_per_page: bool = True

    # Paragraph Reconstruction
    dehyphenation_enabled: bool = True
    preserve_true_hyphens: bool = True
    line_merge_spacing_factor: float = 1.6

    # Header / Footer Handling
    suppress_recurring_headers: bool = True
    recurring_header_min_frequency: float = 0.25  # appears in at least 25% of pages
    header_footer_similarity_threshold: float = 0.82

    # Scalability & Checkpoint
    checkpoint_enabled: bool = True
    save_every_n_pages: int = 1
    max_workers: int = 1  # 1 for stability and sequential memory safety, can increase on beefy hardware

    # UI & Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    def ensure_directories(self) -> None:
        """Ensure all required runtime directories exist."""
        for d in [self.inbox_dir, self.output_dir, self.debug_dir, self.logs_dir, self.checkpoints_dir]:
            d.mkdir(parents=True, exist_ok=True)


default_config = ExtractionConfig()
