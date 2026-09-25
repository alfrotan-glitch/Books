# Windows Desktop Deployment & User Guide
**Digital Book Text Extraction Engine (Production-Grade)**

---

## Quick-Start (3 Simple Steps)

### Step 1: Clone Repository to Windows Desktop
Open **PowerShell** and run:
```powershell
cd "$env:USERPROFILE\Desktop"
git clone -b arena/01a0d9ec-books https://github.com/alfrotan-glitch/Books.git BOOK-TEXT-EXTRACTOR
```

---

### Step 2: One-Click Setup & Desktop Shortcut Installation
Navigate into the newly created folder and double-click:
👉 **`setup.bat`** (or **`نصب_و_راه_اندازی.bat`**)

The setup wizard will:
1. Verify Python 3.10+ installation.
2. Initialize an isolated virtual environment (`.venv`).
3. Install dependencies (RapidOCR, PyMuPDF, headless OpenCV, FastAPI, etc.).
4. **Create a desktop shortcut icon ("Book Text Extractor") directly on your Windows Desktop.**

---

### Step 3: Run the Application
Double-click the **Book Text Extractor** desktop shortcut or run **`run.bat`**.

The engine will start and automatically open your web browser at:
👉 **`http://localhost:8000`**

---

## Features
- **Visual Drag & Drop Upload**: Simply drop PDF files into the browser or copy to `inbox/`.
- **Live Progress & Page Grid**: Watch real-time extraction progress and colored page health status.
- **In-Browser Text Reader**: Inspect and read extracted text immediately without third-party viewers.
- **One-Click Deliverables Download**: Download clean `.txt`, visual quality reports (`.html`), and mathematical zero-loss provenance manifests (`.json`).
- **Resumable Extraction**: Large books stream page-by-page; crashes or interruptions resume automatically without re-processing completed pages.
