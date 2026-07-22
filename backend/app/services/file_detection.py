"""
Detects the real type of an uploaded file (not just trusting the extension)
and decides which downstream pipeline (OCR / parser / CV) should handle it.
"""
import os
import fitz  # PyMuPDF

SUPPORTED_EXTENSIONS = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".xlsx": "xlsx",
    ".xls": "xlsx",
    ".csv": "csv",
    ".txt": "txt",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".zip": "archive",
    ".eml": "email",
    ".msg": "email",
}


def detect_file_type(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return SUPPORTED_EXTENSIONS.get(ext, "unknown")


def pdf_is_scanned(path: str, sample_pages: int = 3) -> bool:
    """
    Heuristic: open the first few pages with PyMuPDF and check whether any
    real text layer exists. If pages contain images but ~no extractable
    text, treat the PDF as scanned and route it through OCR.
    """
    doc = fitz.open(path)
    pages_to_check = min(sample_pages, doc.page_count)
    total_text_len = 0
    for i in range(pages_to_check):
        page = doc.load_page(i)
        total_text_len += len(page.get_text("text").strip())
    doc.close()
    avg_text_len = total_text_len / max(pages_to_check, 1)
    return avg_text_len < 20  # essentially no text per page -> scanned


def classify_document_category(text_sample: str, filename: str) -> str:
    """
    Lightweight keyword-based document classifier used for dashboard
    grouping (Maintenance Report, SOP, Safety Manual, Inspection Report,
    P&ID, OEM Manual, Incident Report, Audit Report, Other).
    """
    text = (text_sample or "").lower()
    name = filename.lower()

    rules = [
        ("p&id", "Engineering Drawing (P&ID)"),
        ("piping and instrumentation", "Engineering Drawing (P&ID)"),
        ("sop", "SOP"),
        ("standard operating procedure", "SOP"),
        ("safety manual", "Safety Manual"),
        ("safety data sheet", "Safety Manual"),
        ("inspection", "Inspection Report"),
        ("incident", "Incident Report"),
        ("near miss", "Incident Report"),
        ("audit", "Audit Report"),
        ("maintenance", "Maintenance Report"),
        ("oem", "OEM Manual"),
        ("manual", "OEM Manual"),
    ]
    for keyword, category in rules:
        if keyword in text or keyword in name:
            return category
    return "General Document"
