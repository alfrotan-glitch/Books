"""
Table Structure Detection and Reconstruction Subsystem.
Detects tables in native and scanned PDF pages and converts them to formatted Markdown.
"""

from typing import Any, Dict, List, Optional, Tuple
import cv2
import numpy as np
import pymupdf

from src.models import BoundingBox, RegionType, SemanticRegion


class TableDetector:
    def __init__(self, min_cells: int = 4):
        self.min_cells = min_cells

    def extract_native_tables(self, page: pymupdf.Page) -> List[Tuple[BoundingBox, str]]:
        """
        Extracts tables from native PDF using PyMuPDF table finder with multiple strategies.
        Requires vector ruling lines to prevent false positive table detection on multi-column text.
        Returns list of (BoundingBox, markdown_table_str).
        """
        results = []
        try:
            # 1. First try lines strategy (grid tables with both horizontal and vertical lines)
            tabs = page.find_tables()
            table_list = list(tabs.tables) if hasattr(tabs, "tables") else list(tabs)

            # 2. Try tables with horizontal line dividers
            if not table_list:
                tabs = page.find_tables(vertical_strategy="text", horizontal_strategy="lines")
                table_list = list(tabs.tables) if hasattr(tabs, "tables") else list(tabs)

            # 3. Try tables with vertical column dividers
            if not table_list:
                tabs = page.find_tables(vertical_strategy="lines", horizontal_strategy="text")
                table_list = list(tabs.tables) if hasattr(tabs, "tables") else list(tabs)

            for tab in table_list:
                raw_cells = tab.extract()
                if not raw_cells or len(raw_cells) < 2:
                    continue

                # Filter out rows that are entirely empty or whitespace
                cells = [
                    row for row in raw_cells
                    if any(c is not None and str(c).strip() for c in row)
                ]
                if len(cells) < 2:
                    continue

                # Format as clean Markdown table
                headers = [str(c).strip().replace("\n", " ") if c is not None else "" for c in cells[0]]
                headers = [h if h else f"Col_{i+1}" for i, h in enumerate(headers)]

                md_lines = []
                md_lines.append("| " + " | ".join(headers) + " |")
                md_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

                for row in cells[1:]:
                    row_vals = [str(c).strip().replace("\n", " ") if c is not None else "" for c in row]
                    # Pad or truncate to match header column count
                    if len(row_vals) < len(headers):
                        row_vals.extend([""] * (len(headers) - len(row_vals)))
                    elif len(row_vals) > len(headers):
                        row_vals = row_vals[: len(headers)]
                    md_lines.append("| " + " | ".join(row_vals) + " |")

                table_md = "\n".join(md_lines)
                rect = tab.bbox
                bbox = BoundingBox(x0=rect[0], y0=rect[1], x1=rect[2], y1=rect[3])
                results.append((bbox, table_md))
        except Exception:
            pass

        return results

    def detect_table_grid_in_image(self, gray: np.ndarray) -> List[BoundingBox]:
        """
        Detects tabular grid lines in scanned document image using morphological kernels.
        """
        h, w = gray.shape
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Detect horizontal lines
        h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(10, w // 25), 1))
        h_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, h_kernel)

        # Detect vertical lines
        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(10, h // 25)))
        v_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, v_kernel)

        # Table grid is intersection / sum of horizontal and vertical lines
        table_grid = cv2.add(h_lines, v_lines)
        contours, _ = cv2.findContours(table_grid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        table_boxes = []
        for c in contours:
            x, y, bw, bh = cv2.boundingRect(c)
            # Table must have sufficient width and height
            if bw > (w * 0.3) and bh > (h * 0.08):
                table_boxes.append(BoundingBox(x0=float(x), y0=float(y), x1=float(x + bw), y1=float(y + bh)))

        return table_boxes
