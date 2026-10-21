#!/usr/bin/env python3
"""Generate a machine-readable receipt for the exact book files produced by this build.

This manifest records technical provenance only, not scientific approval.
"""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
STEM = "Basic_Histology_Learning_Text"
FORMATS = ("pdf", "docx", "epub", "html")
files = {}
for ext in FORMATS:
    p = ROOT / f"{STEM}.{ext}"
    if not p.is_file() or p.stat().st_size == 0:
        raise SystemExit(f"Missing output file: {p}")
    files[p.name] = {
        "bytes": p.stat().st_size,
        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
    }

with pymupdf.open(ROOT / f"{STEM}.pdf") as pdf:
    pdf_info = {"page_count": len(pdf), "outline_entries": len(pdf.get_toc())}

manifest = {
    "title": "Basic Histology: A Learning Text",
    "edition": "First edition (2026)",
    "git_commit": os.environ.get("GITHUB_SHA", "not_provided"),
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "release_status": "editorial_candidate",
    "meaning_of_status": (
        "Build and structural checks are not a substitute for independent scientific "
        "review, EPUB reader testing or full visual/print proof."
    ),
    "pdf": pdf_info,
    "files": files,
}
dest = ROOT / "publication-manifest.json"
dest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Manifest written:", dest)
for name, item in files.items():
    print(name, item["bytes"], item["sha256"])
