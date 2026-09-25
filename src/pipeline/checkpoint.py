"""
Resumable Checkpoint Manager.
Provides crash-safe, transactional page-level persistence using SQLite.
Enables large book extraction to resume exactly where it was interrupted.
"""

import json
from pathlib import Path
import sqlite3
from typing import List, Optional, Set

from src.models import (
    BoundingBox,
    ExtractionMethod,
    PageClassification,
    PageResult,
    QualityMetrics,
    QualityStatus,
    RegionType,
    SemanticRegion,
)


class CheckpointManager:
    def __init__(self, checkpoints_dir: Path, book_id: str):
        self.checkpoints_dir = Path(checkpoints_dir)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        # Safe filename for db
        safe_id = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in book_id)
        self.db_path = self.checkpoints_dir / f"{safe_id}_checkpoint.sqlite"
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS page_checkpoints (
                    page_num INTEGER PRIMARY KEY,
                    classification TEXT,
                    extraction_method TEXT,
                    quality_status TEXT,
                    confidence REAL,
                    text TEXT,
                    regions_json TEXT,
                    error_message TEXT,
                    warnings_json TEXT,
                    tables_count INTEGER,
                    footnotes_count INTEGER,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def save_page(self, pr: PageResult) -> None:
        """Atomically saves or updates a page result."""
        regions_data = [
            {
                "region_id": r.region_id,
                "region_type": r.region_type.value,
                "bbox": r.bbox.to_dict(),
                "confidence": r.confidence,
                "column_index": r.column_index,
                "reading_order_idx": r.reading_order_idx,
                "text": r.text,
            }
            for r in pr.regions
        ]
        regions_json = json.dumps(regions_data, ensure_ascii=False)
        warnings_json = json.dumps(pr.warnings, ensure_ascii=False)

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO page_checkpoints (
                    page_num, classification, extraction_method, quality_status,
                    confidence, text, regions_json, error_message, warnings_json,
                    tables_count, footnotes_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pr.page_num,
                    pr.classification.value,
                    pr.extraction_method.value,
                    pr.quality_status.value,
                    pr.confidence,
                    pr.text,
                    regions_json,
                    pr.error_message,
                    warnings_json,
                    pr.tables_count,
                    pr.footnotes_count,
                ),
            )
            conn.commit()

    def get_completed_pages(self) -> Set[int]:
        """Returns the set of page numbers already successfully processed."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT page_num FROM page_checkpoints WHERE quality_status != 'FAILED'")
            return {row[0] for row in cur.fetchall()}

    def get_all_results(self) -> List[PageResult]:
        """Retrieves all saved page results sorted by page_num."""
        results: List[PageResult] = []
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT page_num, classification, extraction_method, quality_status,
                       confidence, text, regions_json, error_message, warnings_json,
                       tables_count, footnotes_count
                FROM page_checkpoints
                ORDER BY page_num ASC
                """
            )
            for row in cur.fetchall():
                (
                    page_num,
                    classification_str,
                    method_str,
                    status_str,
                    conf,
                    text,
                    reg_json,
                    err_msg,
                    warn_json,
                    t_count,
                    fn_count,
                ) = row

                # Parse regions
                regs: List[SemanticRegion] = []
                try:
                    reg_list = json.loads(reg_json)
                    for item in reg_list:
                        bb = item["bbox"]
                        regs.append(
                            SemanticRegion(
                                region_id=item["region_id"],
                                region_type=RegionType(item["region_type"]),
                                bbox=BoundingBox(x0=bb["x0"], y0=bb["y0"], x1=bb["x1"], y1=bb["y1"]),
                                confidence=item.get("confidence", 1.0),
                                column_index=item.get("column_index", 0),
                                reading_order_idx=item.get("reading_order_idx", 0),
                                text=item.get("text", ""),
                            )
                        )
                except Exception:
                    pass

                warnings = json.loads(warn_json) if warn_json else []

                pr = PageResult(
                    page_num=page_num,
                    classification=PageClassification(classification_str),
                    extraction_method=ExtractionMethod(method_str),
                    text=text,
                    regions=regs,
                    quality_status=QualityStatus(status_str),
                    quality_metrics=QualityMetrics(ocr_confidence=conf),
                    confidence=conf,
                    error_message=err_msg,
                    warnings=warnings,
                    tables_count=t_count or 0,
                    footnotes_count=fn_count or 0,
                )
                results.append(pr)

        return results

    def clear(self) -> None:
        """Resets the checkpoint database."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM page_checkpoints")
            conn.commit()
