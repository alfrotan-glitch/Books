"""
Safe PDF reader and page renderer using PyMuPDF.
Provides streaming page-by-page access and high-fidelity rendering for OCR.
"""

from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple, Union
import numpy as np
import pymupdf


class PDFReader:
    def __init__(self, pdf_path: Union[str, Path]):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        self._doc: Optional[pymupdf.Document] = None

    def __enter__(self) -> "PDFReader":
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def open(self) -> pymupdf.Document:
        if self._doc is None or self._doc.is_closed:
            self._doc = pymupdf.open(str(self.pdf_path))
        return self._doc

    def close(self) -> None:
        if self._doc is not None and not self._doc.is_closed:
            self._doc.close()
            self._doc = None

    @property
    def doc(self) -> pymupdf.Document:
        if self._doc is None or self._doc.is_closed:
            return self.open()
        return self._doc

    @property
    def page_count(self) -> int:
        return len(self.doc)

    @property
    def metadata(self) -> Dict[str, Any]:
        return dict(self.doc.metadata or {})

    @property
    def is_encrypted(self) -> bool:
        return bool(self.doc.is_encrypted)

    def get_page(self, page_num: int) -> pymupdf.Page:
        """page_num is 1-based (1..N)."""
        if page_num < 1 or page_num > self.page_count:
            raise IndexError(f"Page number {page_num} out of bounds (1..{self.page_count})")
        return self.doc.load_page(page_num - 1)

    def stream_pages(self, start_page: int = 1, end_page: Optional[int] = None) -> Generator[Tuple[int, pymupdf.Page], None, None]:
        """Stream pages one-by-one to maintain constant memory footprint."""
        total = self.page_count
        end = total if end_page is None else min(end_page, total)
        for p in range(start_page, end + 1):
            yield p, self.get_page(p)

    def render_page_to_numpy(self, page_num: int, dpi: int = 300) -> np.ndarray:
        """
        Renders a page to an RGB numpy array (H, W, 3) at target DPI.
        Standard PDF resolution is 72 DPI. Target zoom = dpi / 72.0.
        """
        page = self.get_page(page_num)
        zoom = dpi / 72.0
        mat = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, 3))
        return img

    def extract_page_images(self, page_num: int) -> List[Dict[str, Any]]:
        """Extract embedded image metadata and bounding boxes from page."""
        page = self.get_page(page_num)
        image_list = page.get_images(full=True)
        results = []
        for img_info in image_list:
            xref = img_info[0]
            try:
                base_image = self.doc.extract_image(xref)
                results.append({
                    "xref": xref,
                    "width": base_image.get("width", 0),
                    "height": base_image.get("height", 0),
                    "ext": base_image.get("ext", "png"),
                    "colorspace": base_image.get("colorspace", 0),
                    "bpc": base_image.get("bpc", 8),
                })
            except Exception:
                continue
        return results
