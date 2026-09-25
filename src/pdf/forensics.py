"""
PDF Forensics Engine.
Analyzes PDF structure, fonts, text layers, image resolutions, and classifies pages.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pymupdf

from src.config import ExtractionConfig, default_config
from src.models import PageClassification, PageForensics


class PDFForensicsEngine:
    def __init__(self, config: Optional[ExtractionConfig] = None):
        self.config = config or default_config

    def analyze_document_metadata(self, doc: pymupdf.Document, file_path: Path) -> Dict[str, Any]:
        """Extract high-level forensic details for the entire PDF document."""
        page_count = len(doc)
        file_size_bytes = file_path.stat().st_size if file_path.exists() else 0
        metadata = dict(doc.metadata or {})
        
        # Check permissions & encryption
        is_encrypted = doc.is_encrypted
        pdf_version = metadata.get("format", "Unknown")

        return {
            "file_name": file_path.name,
            "file_size_bytes": file_size_bytes,
            "file_size_mb": round(file_size_bytes / (1024 * 1024), 2),
            "page_count": page_count,
            "is_encrypted": is_encrypted,
            "pdf_version": pdf_version,
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "producer": metadata.get("producer", ""),
            "creator": metadata.get("creator", ""),
            "creation_date": metadata.get("creationDate", ""),
            "mod_date": metadata.get("modDate", ""),
        }

    def analyze_page(self, page: pymupdf.Page, page_num: int) -> PageForensics:
        """Perform deep forensic inspection on a single page."""
        rect = page.rect
        width_pt = rect.width
        height_pt = rect.height
        page_area_pt = width_pt * height_pt
        rotation = page.rotation

        raw_text = page.get_text("text") or ""
        char_count = len(raw_text)
        words = raw_text.split()
        word_count = len(words)

        # Inspect fonts
        font_records = page.get_fonts()
        font_names = list({f[3] for f in font_records if len(f) > 3 and f[3]})

        # Inspect character validity and potential corruption
        corrupt_chars = 0
        printable_chars = 0
        cid_pattern_matches = len(re.findall(r"\(cid:\d+\)", raw_text))

        # Check for degraded OCR artifacts in predominantly Latin text
        # (e.g. broken font encodings or old OCR generating À, Á, Â, Ã, Â, etc. in English text)
        accented_corrupt_chars = set("ÀÁÂÃÄÅÆÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæèéêëìíîïðñòóôõöøùúûüýþÿ")
        accented_count = sum(1 for ch in raw_text if ch in accented_corrupt_chars)
        intra_word_dots = len(re.findall(r"[a-zA-Z]\.[a-zA-Z]", raw_text))
        intra_word_underscores = len(re.findall(r"[a-zA-Z]_[a-zA-Z]", raw_text))

        for ch in raw_text:
            code = ord(ch)
            if ch == "\ufffd" or (code < 32 and ch not in "\n\r\t"):
                corrupt_chars += 1
            elif ch.isprintable():
                printable_chars += 1

        corrupt_chars += cid_pattern_matches * 5  # weight CID artifacts heavily
        corrupt_char_ratio = (corrupt_chars / char_count) if char_count > 0 else 0.0
        printable_ratio = (printable_chars / char_count) if char_count > 0 else 0.0

        # Assess whether existing text layer is degraded OCR
        is_degraded_ocr = (
            char_count > 50
            and (accented_count >= 3 or intra_word_dots >= 3 or intra_word_underscores >= 2)
        )

        # Inspect images
        images = page.get_images(full=True)
        image_count = len(images)
        dominant_image_coverage = 0.0
        max_image_dpi = 72.0

        for img_info in images:
            xref = img_info[0]
            try:
                base_img = page.parent.extract_image(xref)
                img_w = base_img.get("width", 0)
                img_h = base_img.get("height", 0)
                if width_pt > 0 and height_pt > 0:
                    dpi_x = (img_w / width_pt) * 72.0
                    dpi_y = (img_h / height_pt) * 72.0
                    estimated_dpi = max(dpi_x, dpi_y)
                    max_image_dpi = max(max_image_dpi, estimated_dpi)
                    coverage = (img_w * img_h) / (width_pt * height_pt * (300 / 72.0)**2)
                    dominant_image_coverage = max(dominant_image_coverage, min(1.0, coverage))
            except Exception:
                continue

        has_native_text = (
            char_count >= self.config.min_native_chars
            and word_count >= self.config.min_native_words
            and corrupt_char_ratio < self.config.max_corrupt_char_ratio
            and printable_ratio >= self.config.min_printable_ratio
            and not is_degraded_ocr  # Degraded OCR must NOT be trusted as clean native text!
        )

        # Detect OCR text characteristics (e.g. font names or hidden text)
        is_ocr_layer = is_degraded_ocr
        if not is_ocr_layer and has_native_text:
            for fn in font_names:
                fn_lower = fn.lower()
                if any(k in fn_lower for k in ["ocr", "tesseract", "omnipage", "type3", "glyphless"]):
                    is_ocr_layer = True
                    break

        notes = []

        # Classification logic
        if rotation in (90, 180, 270):
            classification = PageClassification.ROTATED
            notes.append(f"Page metadata has rotation: {rotation}°")
        elif is_degraded_ocr:
            classification = PageClassification.OCR_EXISTING
            notes.append(
                f"Degraded/corrupted existing OCR layer detected ({accented_count} corrupted accents, {intra_word_dots} intra-word dots). Routing to fresh OCR."
            )
        elif not has_native_text and (image_count > 0 or char_count < self.config.min_native_chars):
            if max_image_dpi > 0 and max_image_dpi < 140:
                classification = PageClassification.LOW_QUALITY_SCAN
                notes.append(f"Scanned image with low DPI: {round(max_image_dpi, 1)}")
            else:
                classification = PageClassification.SCANNED_IMAGE
                notes.append("No valid native text layer found; contains raster image.")
        elif is_ocr_layer:
            classification = PageClassification.OCR_EXISTING
            notes.append("Pre-existing OCR text layer detected.")
        elif has_native_text and image_count > 0 and dominant_image_coverage > 0.20:
            classification = PageClassification.HYBRID
            notes.append("Contains both rich text layer and raster images/figures.")
        elif has_native_text:
            text_blocks = page.get_text("blocks")
            if len(text_blocks) > 8 or len(font_names) > 3:
                classification = PageClassification.COMPLEX_LAYOUT
                notes.append("Native text with multi-block or multi-font complex layout.")
            else:
                classification = PageClassification.NATIVE_TEXT
                notes.append("Clean native text layer.")
        else:
            classification = PageClassification.UNKNOWN
            notes.append("Unclassified page structure.")

        return PageForensics(
            page_num=page_num,
            width_pt=width_pt,
            height_pt=height_pt,
            rotation=rotation,
            char_count=char_count,
            word_count=word_count,
            image_count=image_count,
            fonts=font_names,
            corrupt_char_ratio=corrupt_char_ratio,
            printable_ratio=printable_ratio,
            has_native_text=has_native_text,
            classification=classification,
            estimated_dpi=max_image_dpi,
            notes=notes,
        )
