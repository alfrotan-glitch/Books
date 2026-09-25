"""
Production-Grade Web UI Dashboard for Digital Book Text Extraction Engine.
Designed for non-technical users and office staff.
Supports visual file selection, drag-and-drop upload, live progress tracking,
real-time page status grid, built-in text preview/reader, and one-click deliverables download.
Bilingual Persian (Farsi/Dari) and English interface.
"""

import asyncio
from datetime import datetime
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import time
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import pymupdf

from src.config import default_config
from src.models import ExtractionMethod, QualityStatus
from src.pdf.forensics import PDFForensicsEngine
from src.pipeline.book_pipeline import BookPipeline

app = FastAPI(title="Digital Book Text Extraction Engine", version="2.0.0")

# Global processing manager state
state = {
    "is_busy": False,
    "current_book": "",
    "current_page": 0,
    "total_pages": 0,
    "status_message": "آماده به کار (Ready)",
    "status_message_en": "Ready",
    "start_time": 0.0,
    "elapsed_sec": 0.0,
    "completed_books": [],
    "recent_logs": [],
    "page_grid": [],  # List of {"page": int, "status": str, "method": str, "chars": int}
    "last_error": None,
    "should_cancel": False,
}

_current_task: Optional[asyncio.Task] = None


def add_log(msg_fa: str, msg_en: str = ""):
    ts = datetime.now().strftime("%H:%M:%S")
    entry = f"[{ts}] {msg_fa}" + (f" ({msg_en})" if msg_en else "")
    state["recent_logs"].append(entry)
    if len(state["recent_logs"]) > 50:
        state["recent_logs"].pop(0)


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سیستم هوشمند استخراج متن کتاب - نسخه پروداکشن</title>
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
            --font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Tahoma", sans-serif;
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
            text-align: right;
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
            max-height: 400px;
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
            left: 24px;
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
                <h1>📚 سیستم استخراج و بازسازی متن کتاب از PDF</h1>
                <p>محیط کاربری یک‌پارچه بدون دستورات فنی — ویژه کارمندان و کاربران عادی</p>
            </div>
            <div class="header-controls">
                <button class="btn btn-primary" onclick="processAllInbox()" id="btnProcessAll">
                    <span>⚡ استخراج همه کتاب‌های ورودی</span>
                </button>
            </div>
        </header>

        <!-- Main Workspace Grid -->
        <div class="main-grid">
            <!-- Left Column: File Manager (Inbox) -->
            <div class="card">
                <div class="card-header">
                    <h2>📁 انتخاب و مدیریت کتاب‌ها (Inbox)</h2>
                    <button class="btn btn-sm" onclick="loadInbox()">🔄 بروزرسانی</button>
                </div>

                <!-- Drag & Drop Zone -->
                <div class="dropzone" onclick="document.getElementById('fileInput').click()" id="dropZone">
                    <span class="dropzone-icon">📥</span>
                    <div class="dropzone-title">فایل PDF کتاب را اینجا بکشید و رها کنید</div>
                    <div class="dropzone-desc">یا کلیک کنید تا از داخل کامپیوتر انتخاب نمایید (انتخاب چندتایی مجاز است)</div>
                    <input type="file" id="fileInput" multiple accept=".pdf" style="display:none;" onchange="handleFileSelect(this)">
                </div>

                <div style="font-size: 13px; font-weight: 600; color: var(--text-muted); margin-bottom: 10px;">
                    کتاب‌های آماده برای پردازش:
                </div>
                <ul class="file-list" id="inboxFileList">
                    <li style="color: var(--text-muted); padding: 12px; text-align: center;">در حال بارگذاری لیست کتاب‌ها...</li>
                </ul>
            </div>

            <!-- Right Column: Live Processing Monitor -->
            <div class="card">
                <div class="card-header">
                    <h2>⚙️ وضعیت و پیشرفت زنده پردازش</h2>
                    <span id="busyBadge" class="badge badge-info">آماده (Idle)</span>
                </div>

                <!-- Progress Bar -->
                <div class="progress-container">
                    <div class="progress-header">
                        <span id="currentBookLabel">هیچ کتابی در حال پردازش نیست</span>
                        <span id="pageCountLabel">۰ / ۰ صفحه (۰٪)</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill" id="progressBar"></div>
                    </div>
                </div>

                <!-- Dynamic Status Message -->
                <div class="status-box">
                    <span id="statusSpinner" style="display: none;" class="spinner"></span>
                    <span id="statusMessageText">سیستم آماده دریافت کتاب و شروع استخراج است.</span>
                </div>

                <!-- Visual Page Grid -->
                <div class="page-grid-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 12px; color: var(--text-muted);">شبکه وضعیت تک‌تک صفحات:</span>
                        <div style="font-size: 11px; display: flex; gap: 8px;">
                            <span style="color: #a7f3d0;">■ دیجیتال</span>
                            <span style="color: #bae6fd;">■ اسکن OCR</span>
                            <span style="color: #fef3c7;">■ بازبینی</span>
                        </div>
                    </div>
                    <div class="page-grid" id="pageGridContainer">
                        <div style="color: var(--text-muted); font-size: 12px; padding: 10px; width: 100%; text-align: center;">
                            پس از آغاز استخراج، وضعیت صفحات اینجا به صورت زنده نمایش می‌یابد.
                        </div>
                    </div>
                </div>

                <!-- Live Log Activity -->
                <div style="margin-top: 14px;">
                    <span style="font-size: 12px; color: var(--text-muted);">گزارش لحظه‌ای رویدادها:</span>
                    <div id="logTerminal" style="background: #060911; border: 1px solid var(--border); border-radius: 6px; padding: 10px; font-family: monospace; font-size: 11px; height: 95px; overflow-y: auto; color: #94a3b8; margin-top: 4px;">
                        <div>[آماده] سیستم راه‌اندازی شد.</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Completed Books & Deliverables Section -->
        <div class="card output-card">
            <div class="card-header">
                <h2>✅ کتاب‌های استخراج‌شده و خروجی‌های نهایی</h2>
                <button class="btn btn-sm" onclick="loadOutputs()">🔄 بروزرسانی خروجی‌ها</button>
            </div>

            <div id="outputsContainer">
                <p style="color: var(--text-muted); text-align: center; padding: 20px;">هنوز هیچ کتابی پردازش نشده است.</p>
            </div>

            <!-- Built-in Reader / Text Previewer -->
            <div id="previewSection" style="display: none; margin-top: 24px; border-top: 1px solid var(--border); padding-top: 18px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; font-size: 16px; color: var(--primary);">
                        📖 پیش‌نمایش و خواندن متن: <span id="previewBookTitle" style="color: #fff;"></span>
                    </h3>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn btn-sm" onclick="copyExtractedText()">📋 کپی کل متن</button>
                        <button class="btn btn-sm btn-danger" onclick="closePreview()">✕ بستن</button>
                    </div>
                </div>
                <div class="preview-box" id="previewContent">در حال بارگذاری متن...</div>
            </div>
        </div>
    </div>

    <!-- Notification Toast -->
    <div class="toast" id="toastMessage"></div>

    <script>
        let pollTimer = null;

        // Show Toast
        function showToast(text) {
            const t = document.getElementById('toastMessage');
            t.innerText = text;
            t.style.display = 'block';
            setTimeout(() => { t.style.display = 'none'; }, 3500);
        }

        // Drag & Drop handlers
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
                uploadFiles(input.files);
            }
        }

        async function uploadFiles(files) {
            for (let f of files) {
                if (!f.name.toLowerCase().endsWith('.pdf')) {
                    showToast('خطا: فقط فایل‌های PDF مجاز هستند.');
                    continue;
                }
                const formData = new FormData();
                formData.append('file', f);
                showToast(`در حال ارسال فایل ${f.name}...`);
                try {
                    const res = await fetch('/api/upload', { method: 'POST', body: formData });
                    if (res.ok) {
                        showToast(`فایل ${f.name} با موفقیت به پوشه ورودی اضافه شد.`);
                    }
                } catch(err) {
                    showToast('خطا در ارسال فایل: ' + err);
                }
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
                    list.innerHTML = '<li style="color: var(--text-muted); text-align: center; padding: 14px;">پوشه ورودی خالی است. لطفاً فایل PDF کتاب را داخل کادر بالا بکشید.</li>';
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
                                <div class="file-meta">${f.pages} صفحه &bull; ${f.size_mb} مگابایت</div>
                            </div>
                        </div>
                        <div class="file-actions">
                            <button class="btn btn-sm btn-primary" onclick="processBook('${f.name}')">
                                ▶ استخراج متن
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
            if (!confirm(`آیا از حذف فایل ${filename} مطمئن هستید؟`)) return;
            try {
                const res = await fetch('/api/delete_inbox', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ filename: filename })
                });
                if (res.ok) {
                    showToast(`فایل ${filename} حذف شد.`);
                    loadInbox();
                }
            } catch(e) { showToast('خطا در حذف: ' + e); }
        }

        async function processBook(filename) {
            try {
                const res = await fetch('/api/process', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ filename: filename })
                });
                const data = await res.json();
                if (res.ok) {
                    showToast(`پردازش کتاب ${filename} آغاز شد.`);
                    checkStatus();
                } else {
                    showToast(data.detail || 'خطا در شروع پردازش');
                }
            } catch(e) { showToast('خطا: ' + e); }
        }

        async function processAllInbox() {
            try {
                const res = await fetch('/api/process_all', { method: 'POST' });
                const data = await res.json();
                if (res.ok) {
                    showToast('پردازش کلیه کتاب‌ها آغاز شد.');
                    checkStatus();
                } else {
                    showToast(data.message || 'خطا در پردازش');
                }
            } catch(e) { showToast('خطا: ' + e); }
        }

        async function checkStatus() {
            try {
                const res = await fetch('/api/status');
                const st = await res.json();

                // Labels & Progress
                const btnAll = document.getElementById('btnProcessAll');
                const spinner = document.getElementById('statusSpinner');
                const badge = document.getElementById('busyBadge');

                if (st.is_busy) {
                    btnAll.disabled = true;
                    btnAll.style.opacity = '0.6';
                    spinner.style.display = 'inline-block';
                    badge.className = 'badge badge-warning';
                    badge.innerText = 'در حال کار (Busy)';
                } else {
                    btnAll.disabled = false;
                    btnAll.style.opacity = '1';
                    spinner.style.display = 'none';
                    badge.className = 'badge badge-info';
                    badge.innerText = 'آماده (Idle)';
                }

                document.getElementById('currentBookLabel').innerText = st.current_book ? `کتاب: ${st.current_book}` : 'آماده به کار';
                const pct = st.total_pages > 0 ? Math.round((st.current_page / st.total_pages) * 100) : 0;
                document.getElementById('pageCountLabel').innerText = `${st.current_page} / ${st.total_pages} صفحه (${pct}%)`;
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
                        chip.title = `صفحه ${p.page}: ${p.method} (${p.chars} کاراکتر)`;
                        grid.appendChild(chip);
                    });
                }

                // Update Terminal Logs
                if (st.recent_logs && st.recent_logs.length > 0) {
                    const term = document.getElementById('logTerminal');
                    term.innerHTML = st.recent_logs.map(l => `<div>${l}</div>`).join('');
                    term.scrollTop = term.scrollHeight;
                }

                // If busy, poll every 1 second; otherwise poll every 4 seconds
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
                    container.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 20px;">هنوز هیچ کتابی استخراج نشده است.</p>';
                    return;
                }

                let html = `
                    <table class="output-table">
                        <thead>
                            <tr>
                                <th>نام کتاب</th>
                                <th>تعداد صفحات</th>
                                <th>حجم متن خروجی</th>
                                <th>فایل متنی اصلی (.txt)</th>
                                <th>گزارش بصری کیفیت</th>
                                <th>عملیات</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                data.outputs.forEach(o => {
                    html += `
                        <tr>
                            <td><strong>${o.book_name}</strong></td>
                            <td>${o.pages_count} صفحه</td>
                            <td>${o.char_count_formatted} کاراکتر</td>
                            <td>
                                <a href="/api/download?path=${encodeURIComponent(o.txt_path)}" class="btn btn-sm btn-success">
                                    📥 دانلود TXT
                                </a>
                            </td>
                            <td>
                                ${o.html_path ? `
                                    <a href="/output/${encodeURIComponent(o.book_name)}_report.html" target="_blank" class="btn btn-sm">
                                        📊 مشاهده گزارش
                                    </a>
                                ` : '-'}
                            </td>
                            <td>
                                <button class="btn btn-sm btn-primary" onclick="previewText('${encodeURIComponent(o.txt_path)}', '${o.book_name}')">
                                    👁 مطالعه در سیستم
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
                showToast('خطا در دریافت پیش‌نمایش: ' + e);
            }
        }

        function closePreview() {
            document.getElementById('previewSection').style.display = 'none';
        }

        function copyExtractedText() {
            const text = document.getElementById('previewContent').innerText;
            navigator.clipboard.writeText(text).then(() => {
                showToast('متن کتاب در حافظه کپی شد!');
            }).catch(() => {
                showToast('عدم دسترسی به حافظه کلیپ‌بورد.');
            });
        }

        // Initialize UI
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


@app.get("/api/inbox")
async def get_inbox():
    default_config.ensure_directories()
    results = []
    for pdf in sorted(default_config.inbox_dir.glob("*.pdf")):
        size_mb = round(pdf.stat().st_size / (1024 * 1024), 2)
        # Fast page count check
        page_count = 0
        try:
            with pymupdf.open(str(pdf)) as d:
                page_count = len(d)
        except Exception:
            page_count = 1
        results.append({
            "name": pdf.name,
            "size_mb": size_mb,
            "pages": page_count,
            "path": str(pdf),
        })
    return {"files": results}


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    default_config.ensure_directories()
    dest = default_config.inbox_dir / file.filename
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    add_log(f"فایل {file.filename} در پوشه inbox ذخیره شد.", f"Uploaded {file.filename}")
    return {"status": "success", "filename": file.filename}


@app.post("/api/delete_inbox")
async def delete_inbox(data: Dict[str, str]):
    filename = data.get("filename")
    if not filename:
        raise HTTPException(status_code=400, detail="Filename required")
    path = default_config.inbox_dir / filename
    if path.exists():
        path.unlink()
        add_log(f"فایل {filename} حذف گردید.", f"Deleted {filename}")
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="File not found")


@app.get("/api/status")
async def get_status():
    if state["is_busy"] and state["start_time"] > 0:
        state["elapsed_sec"] = round(time.time() - state["start_time"], 1)
    return state


@app.post("/api/process")
async def process_single(data: Dict[str, str]):
    if state["is_busy"]:
        raise HTTPException(status_code=409, detail="سیستم هم‌اکنون مشغول پردازش کتاب دیگری است.")

    filename = data.get("filename")
    if not filename:
        raise HTTPException(status_code=400, detail="Filename required")

    pdf_path = default_config.inbox_dir / filename
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="فایل در پوشه ورودی یافت نشد.")

    asyncio.create_task(run_extraction_task(pdf_path))
    return {"status": "started", "filename": filename}


@app.post("/api/process_all")
async def process_all():
    if state["is_busy"]:
        raise HTTPException(status_code=409, detail="سیستم هم‌اکنون مشغول پردازش است.")

    pdfs = sorted(default_config.inbox_dir.glob("*.pdf"))
    if not pdfs:
        return {"status": "empty", "message": "هیچ فایل PDF در پوشه ورودی وجود ندارد."}

    asyncio.create_task(run_batch_extraction(pdfs))
    return {"status": "started", "count": len(pdfs)}


async def run_extraction_task(pdf_path: Path):
    global state
    state["is_busy"] = True
    state["current_book"] = pdf_path.name
    state["current_page"] = 0
    state["total_pages"] = 0
    state["start_time"] = time.time()
    state["page_grid"] = []
    state["status_message"] = f"شروع بازرسی و تحلیل لایه‌های {pdf_path.name}..."
    add_log(f"شروع استخراج کتاب {pdf_path.name}", "Started extraction")

    def progress_cb(page_num: int, total: int, msg: str):
        state["current_page"] = page_num
        state["total_pages"] = total
        state["status_message"] = f"صفحه {page_num} از {total}: {msg}"

    try:
        pipeline = BookPipeline(default_config)
        loop = asyncio.get_event_loop()

        # Run extraction in worker thread so FastAPI remains completely responsive!
        report = await loop.run_in_executor(None, pipeline.process_pdf, pdf_path, progress_cb, False)

        # Build page grid
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
        state["status_message"] = f"استخراج کتاب {pdf_path.name} با موفقیت به پایان رسید."
        add_log(f"پایان موفقیت‌آمیز استخراج {pdf_path.name} ({report.total_pages} صفحه)", "Extraction finished")

    except Exception as exc:
        state["last_error"] = str(exc)
        state["status_message"] = f"خطا در پردازش: {exc}"
        add_log(f"خطا در پردازش: {exc}", "Error")
    finally:
        state["is_busy"] = False


async def run_batch_extraction(pdf_list: List[Path]):
    for p in pdf_list:
        await run_extraction_task(p)


@app.get("/api/outputs")
async def get_outputs():
    default_config.ensure_directories()
    outputs = []
    for txt in sorted(default_config.output_dir.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True):
        b_name = txt.stem
        # Exclude temporary benchmark files if present
        if b_name.startswith("bench_"):
            continue

        html_file = default_config.output_dir / f"{b_name}_report.html"
        json_file = default_config.output_dir / f"{b_name}_report.json"

        # Read char count
        char_count = 0
        pages_count = 1
        try:
            with open(txt, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                char_count = len(content)
                # Count pages from headers
                pages_count = max(1, content.count("--- [Page "))
        except Exception:
            pass

        outputs.append({
            "book_name": b_name,
            "txt_path": str(txt),
            "html_path": str(html_file) if html_file.exists() else "",
            "json_path": str(json_file) if json_file.exists() else "",
            "char_count": char_count,
            "char_count_formatted": f"{char_count:,}",
            "pages_count": pages_count,
        })

    return {"outputs": outputs}


@app.get("/api/preview")
async def preview_text(path: str):
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            preview = f.read(12000)  # Read first 12000 chars for smooth reading
        return {"text": preview}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download")
async def download_file(path: str):
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(p, filename=p.name)


@app.get("/output/{filename}")
async def serve_output(filename: str):
    p = default_config.output_dir / filename
    if not p.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(p)
