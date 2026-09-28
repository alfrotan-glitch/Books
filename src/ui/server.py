"""
Web UI Server for Digital Book Text Extractor.
Modern English interface for non-technical users, desktop operators, and automated batch processing.
"""

import asyncio
from collections import Counter
from datetime import datetime
import json
import logging
from pathlib import Path
import shutil
import time
from typing import Any, Dict, List, Optional, Tuple

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import pymupdf

from src.config import default_config
from src.models import (
    BookReport,
    ExtractionMethod,
    PageClassification,
    PageResult,
    QualityStatus,
)
from src.pipeline.book_pipeline import BookPipeline

logger = logging.getLogger("ui_server")

app = FastAPI(title="Book Text Extractor", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global processing state
state: Dict[str, Any] = {
    "is_busy": False,
    "should_cancel": False,
    "current_book": "",
    "current_page": 0,
    "total_pages": 0,
    "status_message": "System is ready to receive books and begin extraction.",
    "start_time": 0.0,
    "elapsed_sec": 0.0,
    "last_error": "",
    "completed_books": [],
    "recent_logs": ["[READY] System initialized."],
    "page_grid": [],
}


def add_log(msg: str, label: str = "INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] [{label}] {msg}"
    state["recent_logs"].append(entry)
    if len(state["recent_logs"]) > 60:
        state["recent_logs"].pop(0)


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Book Text Extractor & Forensic Pipeline</title>
    <style>
        :root {
            --bg: #090d16;
            --surface: #131b2e;
            --surface-card: #1a243b;
            --surface-hover: #22304e;
            --primary: #38bdf8;
            --primary-hover: #0284c7;
            --primary-glow: rgba(56, 189, 248, 0.25);
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --border: #2a3754;
            --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        * { box-sizing: border-box; }
        body {
            font-family: var(--font-family);
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }

        .container { max-width: 1300px; margin: 0 auto; }

        /* Top Header */
        .top-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(135deg, #131b2e 0%, #1a2744 100%);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px 28px;
            margin-bottom: 24px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }
        .header-title h1 {
            margin: 0;
            font-size: 24px;
            color: var(--primary);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .header-title p {
            margin: 6px 0 0 0;
            color: var(--text-muted);
            font-size: 14px;
        }
        .header-controls {
            display: flex;
            gap: 12px;
            align-items: center;
        }

        /* Buttons */
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: var(--surface-card);
            color: var(--text);
            font-family: inherit;
            font-size: 14px;
            font-weight: 600;
            padding: 10px 18px;
            border: 1px solid var(--border);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
        }
        .btn:hover {
            background: var(--surface-hover);
            border-color: var(--primary);
            color: #fff;
        }
        .btn-primary {
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            color: #fff;
            border: none;
            box-shadow: 0 4px 12px var(--primary-glow);
        }
        .btn-primary:hover {
            background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
            color: #090d16;
            box-shadow: 0 6px 16px rgba(56, 189, 248, 0.4);
        }
        .btn-success {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: #fff;
            border: none;
        }
        .btn-success:hover { background: #10b981; }
        .btn-danger {
            background: #ef4444;
            color: #fff;
            border: none;
        }
        .btn-danger:hover { background: #dc2626; }
        .btn-sm { padding: 6px 12px; font-size: 12px; }

        /* Grid Layout */
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1.15fr;
            gap: 24px;
            margin-bottom: 24px;
        }
        @media(max-width: 960px) {
            .main-grid { grid-template-columns: 1fr; }
        }

        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 22px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.25);
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 14px;
            margin-bottom: 18px;
        }
        .card-header h2 {
            margin: 0;
            font-size: 18px;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Upload Dropzone */
        .dropzone {
            border: 2px dashed #3b82f6;
            background: rgba(59, 130, 246, 0.04);
            border-radius: 10px;
            padding: 32px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
            margin-bottom: 18px;
        }
        .dropzone:hover {
            border-color: var(--primary);
            background: rgba(56, 189, 248, 0.08);
            transform: translateY(-2px);
        }
        .dropzone-icon {
            font-size: 38px;
            margin-bottom: 8px;
            display: block;
        }
        .dropzone-title {
            font-size: 16px;
            font-weight: 700;
            color: #fff;
            margin-bottom: 4px;
        }
        .dropzone-desc {
            font-size: 13px;
            color: var(--text-muted);
        }

        /* File List */
        .file-list {
            list-style: none;
            padding: 0;
            margin: 0;
            max-height: 280px;
            overflow-y: auto;
        }
        .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--surface-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px 14px;
            margin-bottom: 10px;
            transition: background 0.2s;
        }
        .file-item:hover { background: var(--surface-hover); }
        .file-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .file-icon { font-size: 22px; color: #ef4444; }
        .file-title { font-weight: 600; font-size: 14px; color: #fff; }
        .file-meta { font-size: 12px; color: var(--text-muted); }
        .file-actions { display: flex; gap: 8px; }

        /* Progress Card */
        .progress-container {
            margin: 20px 0;
        }
        .progress-header {
            display: flex;
            justify-content: space-between;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .progress-track {
            background: var(--border);
            height: 14px;
            border-radius: 7px;
            overflow: hidden;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.4);
        }
        .progress-fill {
            background: linear-gradient(90deg, #0284c7 0%, #38bdf8 100%);
            height: 100%;
            width: 0%;
            transition: width 0.3s ease;
            box-shadow: 0 0 12px var(--primary-glow);
        }
        .status-box {
            background: #0b1120;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px 16px;
            margin-top: 14px;
            font-family: monospace;
            font-size: 13px;
            color: #38bdf8;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        /* Page Grid Tracker */
        .page-grid-card {
            margin-top: 18px;
        }
        .page-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            max-height: 160px;
            overflow-y: auto;
            padding: 8px;
            background: #090d16;
            border: 1px solid var(--border);
            border-radius: 8px;
        }
        .page-chip {
            width: 34px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 700;
            border-radius: 4px;
            background: var(--border);
            color: var(--text-muted);
            cursor: default;
        }
        .page-chip.done-native { background: #065f46; color: #a7f3d0; border: 1px solid #059669; }
        .page-chip.done-ocr { background: #075985; color: #bae6fd; border: 1px solid #0284c7; }
        .page-chip.review { background: #92400e; color: #fef3c7; border: 1px solid #f59e0b; }
        .page-chip.failed { background: #991b1b; color: #fecaca; border: 1px solid #ef4444; }

        /* Output & Deliverables Section */
        .output-card {
            margin-top: 24px;
        }
        .output-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            margin-top: 12px;
        }
        .output-table th, .output-table td {
            padding: 12px 14px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        .output-table th {
            background: var(--surface-card);
            color: var(--text-muted);
            font-weight: 600;
        }
        .output-table tr:hover { background: var(--surface-hover); }

        /* Text Reader Modal / Preview */
        .preview-box {
            background: #070a12;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            max-height: 450px;
            overflow-y: auto;
            white-space: pre-wrap;
            font-family: inherit;
            font-size: 14px;
            line-height: 1.8;
            color: #e2e8f0;
            margin-top: 14px;
        }

        .badge {
            padding: 4px 8px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 700;
        }
        .badge-success { background: #065f46; color: #a7f3d0; }
        .badge-info { background: #075985; color: #bae6fd; }
        .badge-warning { background: #92400e; color: #fef3c7; }
        .badge-danger { background: #991b1b; color: #fecaca; }

        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        .toast {
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: var(--surface-card);
            border: 1px solid var(--border);
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.5);
            display: none;
            z-index: 1000;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Top Header -->
        <header class="top-header">
            <div class="header-title">
                <h1>📚 Digital Book Text Extractor & Forensics Engine</h1>
                <p>Production-Grade OCR, Layout Recovery & Reading Order Pipeline</p>
            </div>
            <div class="header-controls">
                <button class="btn btn-primary" onclick="processAllInbox()" id="btnProcessAll">
                    <span>⚡ Extract All Inbox Books</span>
                </button>
            </div>
        </header>

        <!-- OCR Engine Status Banner -->
        <div id="engineStatusBanner" style="display: flex; align-items: center; justify-content: space-between; padding: 12px 18px; border-radius: 8px; margin-bottom: 20px; border: 1px solid var(--border); background: var(--surface);">
            <div id="engineStatusText" style="font-size: 13px;">Checking OCR engine status...</div>
            <div id="engineActionBtn" style="font-size: 12px;"></div>
        </div>

        <!-- Main Workspace Grid -->
        <div class="main-grid">
            <!-- Left Column: File Manager (Inbox) -->
            <div class="card">
                <div class="card-header">
                    <h2>📁 Book Selection & Management (Inbox)</h2>
                    <button class="btn btn-sm" onclick="loadInbox()">🔄 Refresh</button>
                </div>

                <!-- Drag & Drop Zone -->
                <div class="dropzone" onclick="document.getElementById('fileInput').click()" id="dropZone">
                    <span class="dropzone-icon">📥</span>
                    <div class="dropzone-title">Drag & drop PDF books here</div>
                    <div class="dropzone-desc">or click to browse from computer (multiple selection supported)</div>
                    <div id="uploadProgressContainer" style="display: none; width: 100%; margin-top: 14px; background: rgba(0,0,0,0.25); padding: 10px; border-radius: 8px; border: 1px solid var(--border);">
                        <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px; color: var(--primary);">
                            <span id="uploadStatusText">Uploading file...</span>
                            <span id="uploadPercentText" style="font-weight: 700;">0%</span>
                        </div>
                        <div style="width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">
                            <div id="uploadProgressBar" style="width: 0%; height: 100%; background: linear-gradient(90deg, var(--primary), var(--success)); transition: width 0.15s ease;"></div>
                        </div>
                    </div>
                    <input type="file" id="fileInput" multiple accept=".pdf" style="display:none;" onchange="handleFileSelect(this)">
                </div>

                <div style="font-size: 13px; font-weight: 600; color: var(--text-muted); margin-bottom: 10px;">
                    Books ready for extraction:
                </div>
                <ul class="file-list" id="inboxFileList">
                    <li style="color: var(--text-muted); padding: 12px; text-align: center;">Loading books...</li>
                </ul>
            </div>

            <!-- Right Column: Live Processing Monitor -->
            <div class="card">
                <div class="card-header">
                    <h2>⚙️ Processing Status & Live Monitor</h2>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <span id="elapsedBadge" class="badge" style="display: none; background: #1e293b; color: #94a3b8;">Time: 0s</span>
                        <button id="btnCancel" class="btn btn-sm btn-danger" style="display: none;" onclick="cancelCurrentExtraction()">
                            ⏹ Cancel Operation
                        </button>
                        <span id="busyBadge" class="badge badge-info">Idle</span>
                    </div>
                </div>

                <!-- Progress Bar -->
                <div class="progress-container">
                    <div class="progress-header">
                        <span id="currentBookLabel">No book currently processing</span>
                        <span id="pageCountLabel">0 / 0 pages (0%)</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill" id="progressBar"></div>
                    </div>
                </div>

                <!-- Dynamic Status Message -->
                <div class="status-box">
                    <span id="statusSpinner" style="display: none;" class="spinner"></span>
                    <span id="statusMessageText">System is ready to receive books and begin extraction.</span>
                </div>

                <!-- Visual Page Grid -->
                <div class="page-grid-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 12px; color: var(--text-muted);">Page-by-page Status Grid:</span>
                        <div style="font-size: 11px; display: flex; gap: 8px;">
                            <span style="color: #a7f3d0;">■ Digital</span>
                            <span style="color: #bae6fd;">■ OCR Scan</span>
                            <span style="color: #fef3c7;">■ Review</span>
                        </div>
                    </div>
                    <div class="page-grid" id="pageGridContainer">
                        <div style="color: var(--text-muted); font-size: 12px; padding: 10px; width: 100%; text-align: center;">
                            Page status will appear here live once processing starts.
                        </div>
                    </div>
                </div>

                <!-- Live Log Activity -->
                <div style="margin-top: 14px;">
                    <span style="font-size: 12px; color: var(--text-muted);">Real-Time Event Logs:</span>
                    <div id="logTerminal" style="background: #060911; border: 1px solid var(--border); border-radius: 6px; padding: 10px; font-family: monospace; font-size: 11px; height: 95px; overflow-y: auto; color: #94a3b8; margin-top: 4px;">
                        <div>[READY] System initialized.</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Completed Books & Deliverables Section -->
        <div class="card output-card">
            <div class="card-header">
                <h2>✅ Extracted Books & Deliverables</h2>
                <button class="btn btn-sm" onclick="loadOutputs()">🔄 Refresh Outputs</button>
            </div>

            <div id="outputsContainer">
                <p style="color: var(--text-muted); text-align: center; padding: 20px;">No books processed yet.</p>
            </div>

            <!-- Built-in Reader / Text Previewer -->
            <div id="previewSection" style="display: none; margin-top: 24px; border-top: 1px solid var(--border); padding-top: 18px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; font-size: 16px; color: var(--primary);">
                        📖 Text Preview & Reader: <span id="previewBookTitle" style="color: #fff;"></span>
                    </h3>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn btn-sm" onclick="copyExtractedText()">📋 Copy Text</button>
                        <button class="btn btn-sm btn-danger" onclick="closePreview()">✕ Close</button>
                    </div>
                </div>
                <div class="preview-box" id="previewContent">Loading text...</div>
            </div>
        </div>
    </div>

    <!-- Notification Toast -->
    <div class="toast" id="toastMessage"></div>

    <script>
        let pollTimer = null;

        function showToast(text) {
            const t = document.getElementById('toastMessage');
            t.innerText = text;
            t.style.display = 'block';
            setTimeout(() => { t.style.display = 'none'; }, 3500);
        }

        const dropZone = document.getElementById('dropZone');
        ['dragenter', 'dragover'].forEach(name => {
            dropZone.addEventListener(name, (e) => {
                e.preventDefault();
                dropZone.style.borderColor = '#38bdf8';
                dropZone.style.background = 'rgba(56, 189, 248, 0.12)';
            });
        });
        ['dragleave', 'drop'].forEach(name => {
            dropZone.addEventListener(name, (e) => {
                e.preventDefault();
                dropZone.style.borderColor = '#3b82f6';
                dropZone.style.background = 'rgba(59, 130, 246, 0.04)';
            });
        });
        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                uploadFiles(files);
            }
        });

        function handleFileSelect(input) {
            if (input.files && input.files.length > 0) {
                uploadFiles(Array.from(input.files));
                input.value = '';
            }
        }

        async function uploadFiles(files) {
            const pContainer = document.getElementById('uploadProgressContainer');
            const pBar = document.getElementById('uploadProgressBar');
            const pText = document.getElementById('uploadPercentText');
            const pStatus = document.getElementById('uploadStatusText');

            for (let f of files) {
                if (!f.name.toLowerCase().endsWith('.pdf')) {
                    showToast('Error: Only PDF files are supported.');
                    continue;
                }

                if (pContainer) {
                    pContainer.style.display = 'block';
                    pBar.style.width = '0%';
                    pText.innerText = '0%';
                    pStatus.innerText = `Uploading ${f.name}...`;
                }

                await new Promise((resolve) => {
                    const xhr = new XMLHttpRequest();
                    const formData = new FormData();
                    formData.append('file', f);

                    xhr.upload.addEventListener('progress', (e) => {
                        if (e.lengthComputable && pBar && pText && pStatus) {
                            const pct = Math.round((e.loaded / e.total) * 100);
                            const mbLoaded = (e.loaded / (1024 * 1024)).toFixed(1);
                            const mbTotal = (e.total / (1024 * 1024)).toFixed(1);
                            pBar.style.width = pct + '%';
                            pText.innerText = pct + '%';
                            pStatus.innerText = `Uploading ${f.name} (${mbLoaded}MB of ${mbTotal}MB)...`;
                        }
                    });

                    xhr.addEventListener('load', () => {
                        if (xhr.status >= 200 && xhr.status < 300) {
                            showToast(`File ${f.name} uploaded successfully.`);
                        } else {
                            showToast(`Upload failed for ${f.name}: status ${xhr.status}`);
                        }
                        resolve();
                    });

                    xhr.addEventListener('error', () => {
                        showToast(`Network error uploading ${f.name}`);
                        resolve();
                    });

                    xhr.open('POST', '/api/upload');
                    xhr.send(formData);
                });
            }

            if (pContainer) {
                pContainer.style.display = 'none';
            }
            loadInbox();
        }

        async function loadInbox() {
            try {
                const res = await fetch('/api/inbox');
                const data = await res.json();
                const list = document.getElementById('inboxFileList');
                list.innerHTML = '';
                if (!data.files || data.files.length === 0) {
                    list.innerHTML = '<li style="color: var(--text-muted); text-align: center; padding: 14px;">Inbox folder is empty. Drag and drop PDF books above.</li>';
                    return;
                }
                data.files.forEach(f => {
                    const li = document.createElement('li');
                    li.className = 'file-item';
                    li.innerHTML = `
                        <div class="file-info">
                            <span class="file-icon">📄</span>
                            <div>
                                <div class="file-title">${f.name}</div>
                                <div class="file-meta">${f.pages} pages &bull; ${f.size_mb} MB</div>
                            </div>
                        </div>
                        <div class="file-actions" style="display: flex; gap: 6px; align-items: center;">
                            <input type="text" id="range_${f.name}" placeholder="Range (e.g. 1-20)" style="font-size: 11px; padding: 4px 6px; border-radius: 4px; border: 1px solid var(--border); background: var(--surface-card); color: var(--text); width: 120px;" title="Leave empty for full book, or specify e.g. 1-15">
                            <button class="btn btn-sm btn-primary" onclick="processBook('${f.name}')">
                                ▶ Extract
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="deleteInboxFile('${f.name}')">
                                🗑
                            </button>
                        </div>
                    `;
                    list.appendChild(li);
                });
            } catch(e) {
                console.error('Error loading inbox:', e);
            }
        }

        async function deleteInboxFile(filename) {
            if (!confirm(`Delete ${filename}?`)) return;
            try {
                const res = await fetch('/api/delete_inbox', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ filename: filename })
                });
                if (res.ok) {
                    showToast(`Deleted ${filename}`);
                    loadInbox();
                }
            } catch(e) { showToast('Error deleting file: ' + e); }
        }

        async function processBook(filename) {
            const rangeElem = document.getElementById(`range_${filename}`);
            const rangeVal = rangeElem ? rangeElem.value.trim() : '';
            try {
                const res = await fetch('/api/process', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ filename: filename, page_range: rangeVal })
                });
                const data = await res.json();
                if (res.ok) {
                    showToast(`Started extraction for ${filename}`);
                    checkStatus();
                } else {
                    showToast(data.detail || 'Failed to start extraction');
                }
            } catch(e) { showToast('Error: ' + e); }
        }

        async function cancelCurrentExtraction() {
            if (!confirm('Are you sure you want to stop and cancel the current extraction?')) return;
            try {
                const res = await fetch('/api/cancel', { method: 'POST' });
                const data = await res.json();
                showToast(data.message || 'Cancel requested.');
                document.getElementById('statusMessageText').innerText = 'Canceling extraction... please wait.';
            } catch(e) {
                showToast('Cancel error: ' + e);
            }
        }

        async function processAllInbox() {
            try {
                const res = await fetch('/api/process_all', { method: 'POST' });
                const data = await res.json();
                if (res.ok) {
                    showToast('Started batch extraction for all inbox books.');
                    checkStatus();
                } else {
                    showToast(data.message || 'Failed to start batch extraction');
                }
            } catch(e) { showToast('Error: ' + e); }
        }

        async function checkStatus() {
            try {
                const res = await fetch('/api/status');
                const st = await res.json();

                const btnAll = document.getElementById('btnProcessAll');
                const spinner = document.getElementById('statusSpinner');
                const badge = document.getElementById('busyBadge');

                if (st.is_busy) {
                    btnAll.disabled = true;
                    btnAll.style.opacity = '0.6';
                    spinner.style.display = 'inline-block';
                    badge.className = 'badge badge-warning';
                    badge.innerText = 'Busy';
                    document.getElementById('btnCancel').style.display = 'inline-flex';
                    const elBadge = document.getElementById('elapsedBadge');
                    elBadge.style.display = 'inline-block';
                    elBadge.innerText = `Time: ${st.elapsed_sec || 0}s`;
                } else {
                    btnAll.disabled = false;
                    btnAll.style.opacity = '1';
                    spinner.style.display = 'none';
                    badge.className = 'badge badge-info';
                    badge.innerText = 'Idle';
                    document.getElementById('btnCancel').style.display = 'none';
                    document.getElementById('elapsedBadge').style.display = 'none';
                }

                document.getElementById('currentBookLabel').innerText = st.current_book ? `Book: ${st.current_book}` : 'Ready';
                const pct = st.total_pages > 0 ? Math.round((st.current_page / st.total_pages) * 100) : 0;
                document.getElementById('pageCountLabel').innerText = `${st.current_page} / ${st.total_pages} pages (${pct}%)`;
                document.getElementById('progressBar').style.width = pct + '%';
                document.getElementById('statusMessageText').innerText = st.status_message;

                // Update Page Grid
                if (st.page_grid && st.page_grid.length > 0) {
                    const grid = document.getElementById('pageGridContainer');
                    grid.innerHTML = '';
                    st.page_grid.forEach(p => {
                        const chip = document.createElement('div');
                        chip.className = 'page-chip ' + p.status_class;
                        chip.innerText = p.page;
                        chip.title = `Page ${p.page}: ${p.method} (${p.chars} chars)`;
                        grid.appendChild(chip);
                    });
                }

                // Update Terminal Logs
                if (st.recent_logs && st.recent_logs.length > 0) {
                    const term = document.getElementById('logTerminal');
                    term.innerHTML = st.recent_logs.map(l => `<div>${l}</div>`).join('');
                    term.scrollTop = term.scrollHeight;
                }

                clearTimeout(pollTimer);
                if (st.is_busy) {
                    pollTimer = setTimeout(checkStatus, 1000);
                } else {
                    pollTimer = setTimeout(checkStatus, 4000);
                    loadOutputs();
                }
            } catch(e) {
                console.error(e);
                pollTimer = setTimeout(checkStatus, 4000);
            }
        }

        async function loadOutputs() {
            try {
                const res = await fetch('/api/outputs');
                const data = await res.json();
                const container = document.getElementById('outputsContainer');
                if (!data.outputs || data.outputs.length === 0) {
                    container.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 20px;">No books extracted yet.</p>';
                    return;
                }

                let html = `
                    <table class="output-table">
                        <thead>
                            <tr>
                                <th>Book Title</th>
                                <th>Pages</th>
                                <th>Extracted Characters</th>
                                <th>Clean Text (.txt)</th>
                                <th>Visual Report</th>
                                <th>Provenance Audit</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                data.outputs.forEach(o => {
                    html += `
                        <tr>
                            <td><strong>${o.book_name}</strong></td>
                            <td>${o.pages_count} pages</td>
                            <td>${o.char_count_formatted} chars</td>
                            <td>
                                <a href="/api/download?path=${encodeURIComponent(o.txt_path)}" class="btn btn-sm btn-success">
                                    📥 Download TXT
                                </a>
                            </td>
                            <td>
                                ${o.html_path ? `
                                    <a href="/output/${encodeURIComponent(o.book_name)}_report.html" target="_blank" class="btn btn-sm">
                                        📊 HTML Report
                                    </a>
                                ` : '-'}
                            </td>
                            <td>
                                ${o.prov_path ? `
                                    <a href="/output/${encodeURIComponent(o.book_name)}_provenance.json" target="_blank" class="btn btn-sm" style="background:#1e293b; border-color:#475569;">
                                        📋 JSON Audit
                                    </a>
                                ` : '-'}
                            </td>
                            <td>
                                <button class="btn btn-sm btn-primary" onclick="previewText('${encodeURIComponent(o.txt_path)}', '${o.book_name}')">
                                    👁 Read Text
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="deleteOutputBook('${o.book_name}')" title="Delete output deliverables">
                                    🗑
                                </button>
                            </td>
                        </tr>
                    `;
                });

                html += '</tbody></table>';
                container.innerHTML = html;
            } catch(e) {
                console.error('Error loading outputs:', e);
            }
        }

        async function previewText(encodedPath, bookName) {
            try {
                const res = await fetch(`/api/preview?path=${encodedPath}`);
                const data = await res.json();
                document.getElementById('previewBookTitle').innerText = bookName;
                document.getElementById('previewContent').innerText = data.text;
                const section = document.getElementById('previewSection');
                section.style.display = 'block';
                section.scrollIntoView({ behavior: 'smooth' });
            } catch(e) {
                showToast('Error loading preview: ' + e);
            }
        }

        async function deleteOutputBook(bookName) {
            if (!confirm(`Delete all extracted output files for "${bookName}"?`)) return;
            try {
                const res = await fetch('/api/delete_output', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ book_name: bookName })
                });
                if (res.ok) {
                    showToast(`Deleted outputs for ${bookName}`);
                    loadOutputs();
                }
            } catch(e) {
                showToast('Error deleting output: ' + e);
            }
        }

        function closePreview() {
            document.getElementById('previewSection').style.display = 'none';
        }

        function copyExtractedText() {
            const text = document.getElementById('previewContent').innerText;
            navigator.clipboard.writeText(text).then(() => {
                showToast('Extracted text copied to clipboard!');
            }).catch(() => {
                showToast('Clipboard access denied.');
            });
        }

        async function checkOcrStatus() {
            try {
                const res = await fetch('/api/ocr_info');
                const info = await res.json();
                const banner = document.getElementById('engineStatusBanner');
                const text = document.getElementById('engineStatusText');
                const btn = document.getElementById('engineActionBtn');

                if (info.tesseract_available && info.tesseract_has_persian) {
                    banner.style.background = 'rgba(16, 185, 129, 0.12)';
                    banner.style.borderColor = '#10b981';
                    text.innerHTML = '🟢 <b>Multi-Language OCR Engine Active:</b> Tesseract OCR (fas + ara + eng) is ready for Persian, Dari, Arabic, and English medical text.';
                    btn.innerHTML = '<span class="badge badge-success">Persian/English Ready</span>';
                } else if (info.rapidocr_available) {
                    banner.style.background = 'rgba(245, 158, 11, 0.15)';
                    banner.style.borderColor = '#f59e0b';
                    text.innerHTML = '⚠️ <b>Warning: Only English/Latin OCR (RapidOCR) is active.</b> For Persian/Dari books, run <b>install_tesseract_farsi.bat</b>.';
                    btn.innerHTML = '<span class="badge badge-warning">Persian Model Needed</span>';
                } else {
                    banner.style.background = 'rgba(239, 68, 68, 0.15)';
                    banner.style.borderColor = '#ef4444';
                    text.innerHTML = '❌ <b>No OCR engine detected.</b> Please run <b>install_tesseract_farsi.bat</b>.';
                    btn.innerHTML = '<span class="badge badge-danger">Engine Inactive</span>';
                }
            } catch(e) {
                console.error(e);
            }
        }

        // Initialize UI
        checkOcrStatus();
        loadInbox();
        loadOutputs();
        checkStatus();
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return HTMLResponse(content=DASHBOARD_HTML)


@app.get("/api/ocr_info")
async def get_ocr_info():
    pipeline = BookPipeline(default_config)
    mgr = pipeline.ocr_manager
    tess_avail = mgr._tesseract_available
    has_fas = mgr.tesseract_has_language("fas")
    has_ara = mgr.tesseract_has_language("ara")
    tess_langs = mgr.get_tesseract_languages() if tess_avail else []
    return {
        "rapidocr_available": bool(mgr.rapid_engine is not None),
        "tesseract_available": tess_avail,
        "tesseract_has_persian": has_fas,
        "tesseract_has_arabic": has_ara,
        "tesseract_languages": tess_langs,
    }


_pdf_page_cache: Dict[Tuple[str, float, int], int] = {}


@app.get("/api/inbox")
async def get_inbox():
    default_config.ensure_directories()
    results = []
    for pdf in sorted(default_config.inbox_dir.glob("*.pdf")):
        try:
            stat_info = pdf.stat()
            size_mb = round(stat_info.st_size / (1024 * 1024), 2)
            cache_key = (str(pdf), stat_info.st_mtime, stat_info.st_size)
            if cache_key in _pdf_page_cache:
                page_count = _pdf_page_cache[cache_key]
            else:
                page_count = 0
                try:
                    with pymupdf.open(str(pdf)) as d:
                        page_count = len(d)
                except Exception:
                    page_count = 1
                _pdf_page_cache[cache_key] = page_count

            results.append({
                "name": pdf.name,
                "size_mb": size_mb,
                "pages": page_count,
                "path": str(pdf),
            })
        except Exception:
            continue
    return {"files": results}


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    default_config.ensure_directories()
    dest = default_config.inbox_dir / file.filename
    with open(dest, "wb") as buffer:
        while chunk := await file.read(4 * 1024 * 1024):
            buffer.write(chunk)
    add_log(f"Uploaded {file.filename} to inbox.", "UPLOAD")
    return {"status": "success", "filename": file.filename}


@app.post("/api/delete_inbox")
async def delete_inbox(data: Dict[str, str]):
    filename = data.get("filename")
    if not filename:
        raise HTTPException(status_code=400, detail="Filename required")
    path = default_config.inbox_dir / filename
    if path.exists():
        path.unlink()
        add_log(f"Deleted {filename} from inbox.", "DELETE")
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="File not found")


@app.get("/api/status")
async def get_status():
    if state["is_busy"] and state["start_time"] > 0:
        state["elapsed_sec"] = round(time.time() - state["start_time"], 1)
    return state


@app.post("/api/cancel")
async def cancel_process():
    if not state["is_busy"]:
        return {"status": "idle", "message": "No extraction task is currently running."}
    state["should_cancel"] = True
    state["status_message"] = "Cancellation requested. Stopping worker gracefully..."
    add_log("Extraction cancellation requested by user.", "CANCEL")
    return {"status": "cancelling", "message": "Cancellation request registered."}


@app.post("/api/process")
async def process_single(data: Dict[str, Any]):
    if state["is_busy"]:
        raise HTTPException(status_code=409, detail="System is currently busy extracting another book.")

    filename = data.get("filename")
    if not filename:
        raise HTTPException(status_code=400, detail="Filename required")

    pdf_path = default_config.inbox_dir / filename
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="File not found in inbox.")

    page_range = None
    page_range_str = data.get("page_range")
    if page_range_str and "-" in str(page_range_str):
        try:
            parts = [int(p.strip()) for p in str(page_range_str).split("-")]
            if len(parts) == 2 and parts[0] <= parts[1]:
                page_range = (parts[0], parts[1])
        except Exception:
            page_range = None

    asyncio.create_task(run_extraction_task(pdf_path, page_range=page_range))
    return {"status": "started", "filename": filename}


@app.post("/api/process_all")
async def process_all():
    if state["is_busy"]:
        raise HTTPException(status_code=409, detail="System is currently busy.")

    pdfs = sorted(default_config.inbox_dir.glob("*.pdf"))
    if not pdfs:
        return {"status": "empty", "message": "No PDF files found in inbox."}

    asyncio.create_task(run_batch_extraction(pdfs))
    return {"status": "started", "count": len(pdfs)}


async def run_extraction_task(pdf_path: Path, page_range: Optional[Tuple[int, int]] = None):
    global state
    state["is_busy"] = True
    state["should_cancel"] = False
    state["current_book"] = pdf_path.name
    state["current_page"] = 0
    state["total_pages"] = 0
    state["start_time"] = time.time()
    state["elapsed_sec"] = 0.0
    state["page_grid"] = []
    
    range_msg = f" (Pages {page_range[0]} to {page_range[1]})" if page_range else ""
    state["status_message"] = f"Analyzing {pdf_path.name}{range_msg}..."
    add_log(f"Starting extraction for {pdf_path.name}{range_msg}", "START")

    def progress_cb(page_num: int, total: int, msg: str):
        state["current_page"] = page_num
        state["total_pages"] = total
        state["status_message"] = f"Page {page_num}/{total}: {msg}"

    def should_cancel_check() -> bool:
        return state.get("should_cancel", False)

    try:
        pipeline = BookPipeline(default_config)
        loop = asyncio.get_event_loop()

        report = await loop.run_in_executor(
            None,
            lambda: pipeline.process_pdf(
                pdf_path,
                progress_cb,
                force_reprocess=True,
                should_cancel_cb=should_cancel_check,
                page_range=page_range,
            )
        )

        grid = []
        for pr in report.page_results:
            cls_name = "done-native"
            if pr.extraction_method in (ExtractionMethod.OCR_RAPIDOCR, ExtractionMethod.OCR_TESSERACT):
                cls_name = "done-ocr"
            if pr.quality_status == QualityStatus.REVIEW_RECOMMENDED:
                cls_name = "review"
            elif pr.quality_status == QualityStatus.FAILED:
                cls_name = "failed"

            grid.append({
                "page": pr.page_num,
                "status_class": cls_name,
                "method": pr.extraction_method.value,
                "chars": len(pr.text),
            })

        state["page_grid"] = grid
        state["completed_books"].append(report.book_name)

        if state.get("should_cancel"):
            state["status_message"] = f"Extraction of {pdf_path.name} was canceled by user."
            add_log(f"Extraction of {pdf_path.name} was canceled.", "CANCELED")
        else:
            state["status_message"] = f"Successfully extracted {pdf_path.name}."
            add_log(f"Finished extraction for {pdf_path.name} ({report.total_pages} pages).", "COMPLETE")

    except Exception as exc:
        state["last_error"] = str(exc)
        state["status_message"] = f"Extraction error: {exc}"
        add_log(f"Extraction error: {exc}", "ERROR")
    finally:
        state["is_busy"] = False
        state["should_cancel"] = False


async def run_batch_extraction(pdf_list: List[Path]):
    for p in pdf_list:
        await run_extraction_task(p)


@app.get("/api/outputs")
async def get_outputs():
    default_config.ensure_directories()
    outputs = []
    for txt in sorted(default_config.output_dir.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True):
        b_name = txt.stem
        if b_name.startswith("bench_"):
            continue

        html_file = default_config.output_dir / f"{b_name}_report.html"
        json_file = default_config.output_dir / f"{b_name}_report.json"
        prov_file = default_config.output_dir / f"{b_name}_provenance.json"

        char_count = 0
        pages_count = 1
        try:
            with open(txt, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                char_count = len(content)
                pages_count = max(1, content.count("--- [Page "))
        except Exception:
            pass

        outputs.append({
            "book_name": b_name,
            "txt_path": str(txt),
            "html_path": str(html_file) if html_file.exists() else "",
            "json_path": str(json_file) if json_file.exists() else "",
            "prov_path": str(prov_file) if prov_file.exists() else "",
            "char_count": char_count,
            "char_count_formatted": f"{char_count:,}",
            "pages_count": pages_count,
        })

    return {"outputs": outputs}


@app.get("/api/preview")
async def preview_text(path: str):
    p = Path(path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Text deliverable not found.")
    try:
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()[:400]
            return {"text": "".join(lines)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/delete_output")
async def delete_output(data: Dict[str, str]):
    book_name = data.get("book_name")
    if not book_name:
        raise HTTPException(status_code=400, detail="Book name required")

    default_config.ensure_directories()
    deleted_files = []
    patterns = [
        f"{book_name}.txt",
        f"{book_name}_report.html",
        f"{book_name}_report.json",
        f"{book_name}_provenance.json",
    ]
    for pat in patterns:
        f = default_config.output_dir / pat
        if f.exists():
            f.unlink()
            deleted_files.append(pat)

    # Purge checkpoints for clean re-extraction
    cp_file = default_config.checkpoints_dir / f"{book_name}_checkpoint.json"
    if cp_file.exists():
        cp_file.unlink()
        deleted_files.append(cp_file.name)

    add_log(f"Deleted outputs and checkpoints for book: {book_name}", "PURGE")
    return {"status": "deleted", "book_name": book_name, "files": deleted_files}


@app.get("/api/download")
async def download_file(path: str):
    p = Path(path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(p, filename=p.name, media_type="text/plain; charset=utf-8")


# Mount output static folder
default_config.ensure_directories()
app.mount("/output", StaticFiles(directory=str(default_config.output_dir)), name="output")
