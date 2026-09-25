"""
Reporting Subsystem.
Generates comprehensive reports in JSON, HTML, CSV, and TXT formats.
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from jinja2 import Template

from src.models import BookReport, PageResult, QualityStatus
from src.validation.verifier import VerificationSummary


HTML_REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Extraction Report - {{ report.book_name }}</title>
    <style>
        :root {
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #1e293b;
            --text-muted: #64748b;
            --primary: #3b82f6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --border: #e2e8f0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 24px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid var(--border);
            padding-bottom: 16px;
            margin-bottom: 24px;
        }
        .header h1 {
            margin: 0;
            font-size: 26px;
            color: #0f172a;
        }
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-success { background-color: #d1fae5; color: #065f46; }
        .badge-warning { background-color: #fef3c7; color: #92400e; }
        .badge-danger { background-color: #fee2e2; color: #991b1b; }
        .badge-info { background-color: #e0f2fe; color: #075985; }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .stat-val {
            font-size: 28px;
            font-weight: 700;
            margin-top: 4px;
        }
        .stat-label {
            font-size: 13px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .section-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .section-card h2 {
            margin-top: 0;
            font-size: 18px;
            border-bottom: 1px solid var(--border);
            padding-bottom: 10px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        th, td {
            text-align: left;
            padding: 10px 12px;
            border-bottom: 1px solid var(--border);
        }
        th {
            background-color: #f1f5f9;
            color: #475569;
            font-weight: 600;
        }
        tr:hover {
            background-color: #f8fafc;
        }
        .mono {
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 13px;
        }
        .alert-box {
            background-color: #fffbeb;
            border-left: 4px solid var(--warning);
            padding: 12px 16px;
            margin-bottom: 16px;
            border-radius: 4px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>Digital Book Extraction Report</h1>
                <p style="margin: 4px 0 0 0; color: var(--text-muted);">
                    Book: <strong>{{ report.book_name }}</strong> &bull; Processed in {{ report.processing_time_sec }}s
                </p>
            </div>
            <div>
                {% if report.failed_pages == 0 and report.needs_review_pages == 0 %}
                    <span class="badge badge-success" style="font-size: 14px; padding: 6px 14px;">100% SUCCESS</span>
                {% elif report.failed_pages > 0 %}
                    <span class="badge badge-danger" style="font-size: 14px; padding: 6px 14px;">{{ report.failed_pages }} ERRORS</span>
                {% else %}
                    <span class="badge badge-warning" style="font-size: 14px; padding: 6px 14px;">{{ report.needs_review_pages }} REVIEW</span>
                {% endif %}
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Pages</div>
                <div class="stat-val" style="color: var(--primary);">{{ report.total_pages }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Native Text Pages</div>
                <div class="stat-val" style="color: #6366f1;">{{ report.native_pages }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">OCR Pages</div>
                <div class="stat-val" style="color: #0ea5e9;">{{ report.ocr_pages }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Successful</div>
                <div class="stat-val" style="color: var(--success);">{{ report.successful_pages }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Needs Review</div>
                <div class="stat-val" style="color: var(--warning);">{{ report.needs_review_pages }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Failed</div>
                <div class="stat-val" style="color: var(--danger);">{{ report.failed_pages }}</div>
            </div>
        </div>

        {% if report.review_pages_list or report.failed_pages_list %}
        <div class="section-card">
            <h2>Pages Requiring Attention</h2>
            {% if report.failed_pages_list %}
            <div class="alert-box" style="border-left-color: var(--danger); background-color: #fef2f2;">
                <strong>Failed Pages:</strong> {{ report.failed_pages_list | join(', ') }}
            </div>
            {% endif %}
            {% if report.review_pages_list %}
            <div class="alert-box">
                <strong>Review Recommended Pages:</strong> {{ report.review_pages_list | join(', ') }}
            </div>
            {% endif %}
        </div>
        {% endif %}

        <div class="section-card">
            <h2>System & Layout Forensics</h2>
            <div style="display: flex; gap: 32px; flex-wrap: wrap;">
                <div>
                    <strong>OCR Engines Used:</strong>
                    {{ report.ocr_engines_used | join(', ') if report.ocr_engines_used else 'None (Native Only)' }}
                </div>
                <div>
                    <strong>Layouts Detected:</strong>
                    {% for k, v in report.layout_types.items() %}
                        {{ k }}: {{ v }} &nbsp;
                    {% endfor %}
                </div>
                <div>
                    <strong>Languages Detected:</strong>
                    {% for k, v in report.detected_languages.items() %}
                        {{ k }}: {{ v }} &nbsp;
                    {% endfor %}
                </div>
            </div>
        </div>

        <div class="section-card">
            <h2>Page Breakdown</h2>
            <table>
                <thead>
                    <tr>
                        <th>Page</th>
                        <th>Classification</th>
                        <th>Method</th>
                        <th>Status</th>
                        <th>Columns</th>
                        <th>Characters</th>
                        <th>Confidence</th>
                        <th>Details / Warnings</th>
                    </tr>
                </thead>
                <tbody>
                    {% for pr in report.page_results %}
                    <tr>
                        <td><strong>#{{ pr.page_num }}</strong></td>
                        <td><span class="mono">{{ pr.classification.value }}</span></td>
                        <td>{{ pr.extraction_method.value }}</td>
                        <td>
                            {% if pr.quality_status.value == 'HIGH_CONFIDENCE' or pr.quality_status.value == 'GOOD' %}
                                <span class="badge badge-success">{{ pr.quality_status.value }}</span>
                            {% elif pr.quality_status.value == 'REVIEW_RECOMMENDED' %}
                                <span class="badge badge-warning">{{ pr.quality_status.value }}</span>
                            {% else %}
                                <span class="badge badge-danger">{{ pr.quality_status.value }}</span>
                            {% endif %}
                        </td>
                        <td>{{ pr.column_count }} col</td>
                        <td>{{ pr.text | length }}</td>
                        <td>{{ "%.1f" | format(pr.confidence * 100) }}%</td>
                        <td style="color: var(--text-muted); font-size: 13px;">
                            {% if pr.error_message %}
                                <span style="color: var(--danger);">{{ pr.error_message }}</span>
                            {% elif pr.warnings %}
                                {{ pr.warnings | join('; ') }}
                            {% else %}
                                OK
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""


class ReportGenerator:
    @staticmethod
    def generate_all_reports(
        report: BookReport,
        output_dir: Path,
        verification: Optional[VerificationSummary] = None,
    ) -> Dict[str, str]:
        """
        Writes JSON, HTML, CSV, and errors.json report files.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        base_name = report.book_name

        # 1. JSON Report
        json_path = output_dir / f"{base_name}_report.json"
        report_dict = report.to_dict()
        if verification:
            report_dict["verification"] = verification.to_dict()
        report_dict["page_results"] = [pr.to_dict() for pr in report.page_results]

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        # 2. HTML Report
        html_path = output_dir / f"{base_name}_report.html"
        template = Template(HTML_REPORT_TEMPLATE)
        html_content = template.render(report=report, verification=verification)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # 3. CSV Report
        csv_path = output_dir / f"{base_name}_pages.csv"
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "page_num",
                "classification",
                "extraction_method",
                "quality_status",
                "confidence",
                "char_count",
                "column_count",
                "tables_count",
                "footnotes_count",
                "error_message",
                "warnings",
            ])
            for pr in report.page_results:
                writer.writerow([
                    pr.page_num,
                    pr.classification.value,
                    pr.extraction_method.value,
                    pr.quality_status.value,
                    round(pr.confidence, 3),
                    len(pr.text),
                    pr.column_count,
                    pr.tables_count,
                    pr.footnotes_count,
                    pr.error_message or "",
                    "; ".join(pr.warnings) if pr.warnings else "",
                ])

        # 4. Errors JSON
        errors_path = output_dir / f"{base_name}_errors.json"
        errors_list = [
            pr.to_dict()
            for pr in report.page_results
            if pr.quality_status == QualityStatus.FAILED or pr.error_message
        ]
        with open(errors_path, "w", encoding="utf-8") as f:
            json.dump(errors_list, f, indent=2, ensure_ascii=False)

        report.report_json_path = str(json_path)
        report.report_html_path = str(html_path)
        report.page_status_csv_path = str(csv_path)
        report.errors_json_path = str(errors_path)

        return {
            "json": str(json_path),
            "html": str(html_path),
            "csv": str(csv_path),
            "errors": str(errors_path),
        }
