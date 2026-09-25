"""
FastAPI Web Dashboard for Windows and Browser-based Document AI Extraction.
Provides one-click processing, inbox management, live progress tracking,
error inspection, and instant output text viewing.
"""

import asyncio
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from src.config import default_config
from src.pipeline.book_pipeline import BookPipeline

app = FastAPI(title="Digital Book Extraction System", version="1.0.0")

# Global processing state
processing_state = {
    "is_busy": False,
    "current_book": "",
    "current_page": 0,
    "total_pages": 0,
    "status_message": "Idle",
    "completed_books": [],
    "last_error": None,
}


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Book Text Extraction System</title>
    <style>
        :root {
            --bg: #0f172a;
            --surface: #1e293b;
            --surface-hover: #334155;
            --primary: #38bdf8;
            --primary-hover: #0284c7;
            --success: #34d399;
            --warning: #fbbf24;
            --danger: #f87171;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --border: #334155;
        }
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 24px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 20px;
            margin-bottom: 24px;
        }
        .header h1 { margin: 0; font-size: 24px; color: var(--primary); }
        .subtitle { color: var(--text-muted); font-size: 14px; margin-top: 4px; }
        
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
        @media(max-width: 800px) { .grid { grid-template-columns: 1fr; } }
        
        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        }
        .card h2 { margin-top: 0; font-size: 18px; border-bottom: 1px solid var(--border); padding-bottom: 10px; }
        
        .btn {
            background: var(--primary);
            color: #0f172a;
            font-weight: 600;
            border: none;
            border-radius: 6px;
            padding: 10px 18px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 14px;
        }
        .btn:hover { background: var(--primary-hover); color: #fff; }
        .btn-success { background: var(--success); }
        .btn-success:hover { background: #059669; }
        .btn-danger { background: var(--danger); color: #fff; }
        
        .file-list { list-style: none; padding: 0; margin: 16px 0; }
        .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 14px;
            background: rgba(0,0,0,0.2);
            border: 1px solid var(--border);
            border-radius: 6px;
            margin-bottom: 8px;
        }
        .badge {
            padding: 3px 8px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 600;
            background: var(--primary);
            color: #0f172a;
        }
        .progress-bar-bg {
            background: var(--border);
            height: 12px;
            border-radius: 6px;
            overflow: hidden;
            margin-top: 10px;
        }
        .progress-bar-fill {
            background: var(--primary);
            height: 100%;
            width: 0%;
            transition: width 0.3s;
        }
        .status-box {
            background: rgba(0,0,0,0.3);
            border: 1px solid var(--border);
            padding: 14px;
            border-radius: 6px;
            margin-top: 14px;
            font-family: monospace;
            font-size: 13px;
        }
        .dropzone {
            border: 2px dashed var(--border);
            border-radius: 8px;
            padding: 30px;
            text-align: center;
            cursor: pointer;
            margin-bottom: 16px;
            transition: border 0.2s;
        }
        .dropzone:hover { border-color: var(--primary); }
        pre.preview-box {
            background: #090d16;
            padding: 14px;
            border-radius: 6px;
            max-height: 350px;
            overflow-y: auto;
            font-size: 12px;
            border: 1px solid var(--border);
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>Digital Book Extraction Engine</h1>
                <div class="subtitle">Production-Grade PDF Forensics, Multi-Column & Layout Reconstruction System</div>
            </div>
            <div>
                <button class="btn btn-success" onclick="processAllInbox()">Extract All Inbox PDFs</button>
            </div>
        </div>

        <div class="grid">
            <!-- Inbox Card -->
            <div class="card">
                <h2>1. Inbox (Input PDFs)</h2>
                <div class="dropzone" onclick="document.getElementById('uploadInput').click()">
                    <p style="margin: 0 0 6px 0; font-weight: 600;">Click to upload PDF or drop file in <code>inbox/</code></p>
                    <span style="font-size: 12px; color: var(--text-muted);">Supports Native, Scanned, CamScanner, Multi-column, Hybrid</span>
                    <input type="file" id="uploadInput" style="display: none;" accept=".pdf" onchange="uploadPDF(this)">
                </div>

                <h3>Available in <code>inbox/</code>:</h3>
                <ul class="file-list" id="inboxList">
                    <li style="color: var(--text-muted);">Loading files...</li>
                </ul>
            </div>

            <!-- Live Status Card -->
            <div class="card">
                <h2>2. Processing Status & Checkpoint</h2>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span id="statusLabel">Status: <strong>Idle</strong></span>
                    <span id="pageProgressLabel">0 / 0 pages</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" id="progressBar"></div>
                </div>
                <div class="status-box" id="statusMessage">
                    Ready to process books.
                </div>

                <div style="margin-top: 16px; display: flex; gap: 10px;">
                    <button class="btn" onclick="checkStatus()">Refresh Status</button>
                </div>
            </div>
        </div>

        <div style="margin-top: 24px;" class="card">
            <h2>3. Completed Books & Deliverables</h2>
            <div id="outputList">
                <p style="color: var(--text-muted);">No outputs generated yet.</p>
            </div>

            <div id="previewContainer" style="display: none; margin-top: 20px;">
                <h3>Output Preview: <span id="previewTitle" style="color: var(--primary);"></span></h3>
                <pre class="preview-box" id="previewText"></pre>
            </div>
        </div>
    </div>

    <script>
        async function loadInbox() {
            try {
                const res = await fetch('/api/inbox');
                const data = await res.json();
                const list = document.getElementById('inboxList');
                list.innerHTML = '';
                if (data.files.length === 0) {
                    list.innerHTML = '<li style="color: var(--text-muted); padding: 8px;">No PDFs in inbox/. Drop a PDF to begin.</li>';
                } else {
                    data.files.forEach(f => {
                        const li = document.createElement('li');
                        li.className = 'file-item';
                        li.innerHTML = `
                            <div>
                                <strong>${f.name}</strong>
                                <span style="font-size: 12px; color: var(--text-muted); margin-left: 8px;">(${f.size_mb} MB)</span>
                            </div>
                            <button class="btn" style="padding: 6px 12px; font-size: 12px;" onclick="processBook('${f.name}')">Process Book</button>
                        `;
                        list.appendChild(li);
                    });
                }
            } catch(e) { console.error(e); }
        }

        async function loadOutputs() {
            try {
                const res = await fetch('/api/outputs');
                const data = await res.json();
                const container = document.getElementById('outputList');
                if (data.outputs.length === 0) {
                    container.innerHTML = '<p style="color: var(--text-muted);">No outputs generated yet.</p>';
                    return;
                }
                let html = '<table style="width: 100%; border-collapse: collapse; font-size: 14px;">';
                html += '<tr style="border-bottom: 1px solid var(--border); text-align: left;"><th style="padding: 8px;">Book Name</th><th>TXT Deliverable</th><th>HTML Report</th><th>JSON Report</th><th>Actions</th></tr>';
                data.outputs.forEach(item => {
                    html += `
                        <tr style="border-bottom: 1px solid var(--border);">
                            <td style="padding: 10px 8px;"><strong>${item.book_name}</strong></td>
                            <td><a href="/api/download?path=${encodeURIComponent(item.txt_path)}" style="color: var(--primary);">Download .txt</a></td>
                            <td><a href="/output/${item.book_name}_report.html" target="_blank" style="color: var(--success);">View Report</a></td>
                            <td><a href="/api/download?path=${encodeURIComponent(item.json_path)}" style="color: var(--text-muted);">Download .json</a></td>
                            <td><button class="btn" style="padding: 4px 10px; font-size: 12px;" onclick="previewText('${item.txt_path}', '${item.book_name}')">Preview Text</button></td>
                        </tr>
                    `;
                });
                html += '</table>';
                container.innerHTML = html;
            } catch(e) { console.error(e); }
        }

        async function previewText(path, name) {
            try {
                const res = await fetch(`/api/preview?path=${encodeURIComponent(path)}`);
                const data = await res.json();
                document.getElementById('previewTitle').innerText = name + '.txt';
                document.getElementById('previewText').innerText = data.text;
                document.getElementById('previewContainer').style.display = 'block';
                document.getElementById('previewContainer').scrollIntoView({ behavior: 'smooth' });
            } catch(e) { alert("Error previewing: " + e); }
        }

        async function uploadPDF(input) {
            if (!input.files || input.files.length === 0) return;
            const file = input.files[0];
            const formData = new FormData();
            formData.append("file", file);
            document.getElementById('statusMessage').innerText = `Uploading ${file.name}...`;
            try {
                const res = await fetch('/api/upload', { method: 'POST', body: formData });
                if (res.ok) {
                    loadInbox();
                    document.getElementById('statusMessage').innerText = `Uploaded ${file.name} to inbox.`;
                }
            } catch(e) { alert("Upload error: " + e); }
        }

        async function processBook(filename) {
            try {
                await fetch('/api/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filename: filename })
                });
                checkStatus();
            } catch(e) { alert("Error: " + e); }
        }

        async function processAllInbox() {
            try {
                await fetch('/api/process_all', { method: 'POST' });
                checkStatus();
            } catch(e) { alert("Error: " + e); }
        }

        async function checkStatus() {
            try {
                const res = await fetch('/api/status');
                const st = await res.json();
                document.getElementById('statusLabel').innerHTML = `Status: <strong>${st.is_busy ? 'Processing' : 'Idle'}</strong>`;
                document.getElementById('pageProgressLabel').innerText = `${st.current_page} / ${st.total_pages} pages`;
                document.getElementById('statusMessage').innerText = st.status_message;

                const pct = st.total_pages > 0 ? (st.current_page / st.total_pages) * 100 : 0;
                document.getElementById('progressBar').style.width = pct + '%';

                if (st.is_busy) {
                    setTimeout(checkStatus, 1500);
                } else {
                    loadInbox();
                    loadOutputs();
                }
            } catch(e) { console.error(e); }
        }

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
async def get_inbox_files():
    default_config.ensure_directories()
    files = []
    for p in sorted(default_config.inbox_dir.glob("*.pdf")):
        size_mb = round(p.stat().st_size / (1024 * 1024), 2)
        files.append({"name": p.name, "size_mb": size_mb})
    return {"files": files}


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    default_config.ensure_directories()
    dest = default_config.inbox_dir / file.filename
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": "success", "filename": file.filename}


@app.get("/api/status")
async def get_status():
    return processing_state


@app.post("/api/process")
async def process_book_api(data: Dict[str, str]):
    filename = data.get("filename")
    if not filename:
        raise HTTPException(status_code=400, detail="Filename required")

    pdf_path = default_config.inbox_dir / filename
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="File not found in inbox")

    if processing_state["is_busy"]:
        raise HTTPException(status_code=409, detail="A processing task is currently running")

    asyncio.create_task(run_pipeline_task(pdf_path))
    return {"status": "started", "filename": filename}


@app.post("/api/process_all")
async def process_all_api():
    if processing_state["is_busy"]:
        raise HTTPException(status_code=409, detail="A processing task is currently running")

    pdfs = sorted(default_config.inbox_dir.glob("*.pdf"))
    if not pdfs:
        return {"status": "no_files", "message": "No PDFs in inbox"}

    asyncio.create_task(run_all_pipeline_tasks(pdfs))
    return {"status": "started", "count": len(pdfs)}


async def run_pipeline_task(pdf_path: Path):
    global processing_state
    processing_state["is_busy"] = True
    processing_state["current_book"] = pdf_path.name
    processing_state["current_page"] = 0
    processing_state["total_pages"] = 0
    processing_state["status_message"] = f"Initializing {pdf_path.name}..."

    def progress(page_num: int, total: int, msg: str):
        processing_state["current_page"] = page_num
        processing_state["total_pages"] = total
        processing_state["status_message"] = msg

    try:
        pipeline = BookPipeline(default_config)
        # Run blocking pipeline in executor
        loop = asyncio.get_event_loop()
        report = await loop.run_in_executor(None, pipeline.process_pdf, pdf_path, progress, False)
        processing_state["completed_books"].append(report.book_name)
        processing_state["status_message"] = f"Finished {pdf_path.name} successfully."
    except Exception as e:
        processing_state["last_error"] = str(e)
        processing_state["status_message"] = f"Error: {e}"
    finally:
        processing_state["is_busy"] = False


async def run_all_pipeline_tasks(pdfs: List[Path]):
    for p in pdfs:
        await run_pipeline_task(p)


@app.get("/api/outputs")
async def get_outputs():
    default_config.ensure_directories()
    outputs = []
    for txt in sorted(default_config.output_dir.glob("*.txt")):
        b_name = txt.stem
        html_file = default_config.output_dir / f"{b_name}_report.html"
        json_file = default_config.output_dir / f"{b_name}_report.json"
        outputs.append({
            "book_name": b_name,
            "txt_path": str(txt),
            "html_path": str(html_file) if html_file.exists() else "",
            "json_path": str(json_file) if json_file.exists() else "",
        })
    return {"outputs": outputs}


@app.get("/api/preview")
async def preview_output(path: str):
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            # First 5000 chars
            preview = f.read(5000)
        return {"text": preview}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download")
async def download_output(path: str):
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(p, filename=p.name)


@app.get("/output/{filename}")
async def serve_output_file(filename: str):
    p = default_config.output_dir / filename
    if not p.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(p)
