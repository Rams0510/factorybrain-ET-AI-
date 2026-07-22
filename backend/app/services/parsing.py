"""
Extracts text (and tables, where relevant) from every supported document
type. Scanned PDFs / images are routed to the OCR service by the caller
(app.services.pipeline) before this module is invoked.
"""
import fitz  # PyMuPDF
import pdfplumber
import docx
import openpyxl
import pandas as pd

from app.services.ocr import ocr_image_file


def parse_pdf_text(path: str) -> str:
    """Extract native text layer using PyMuPDF (fast path for digital PDFs)."""
    doc = fitz.open(path)
    parts = []
    for i in range(doc.page_count):
        page = doc.load_page(i)
        parts.append(f"\n\n--- Page {i + 1} ---\n\n{page.get_text('text')}")
    doc.close()
    return "".join(parts)


def parse_pdf_tables(path: str) -> list[dict]:
    """Extract tables from a PDF using pdfplumber, returned as list of
    {page, table_index, rows} so entity extraction / display can use them."""
    tables_out = []
    with pdfplumber.open(path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for t_index, table in enumerate(tables):
                tables_out.append({
                    "page": page_index + 1,
                    "table_index": t_index,
                    "rows": table,
                })
    return tables_out


def parse_docx(path: str) -> str:
    document = docx.Document(path)
    parts = [p.text for p in document.paragraphs if p.text.strip()]
    for table in document.tables:
        for row in table.rows:
            parts.append(" | ".join(cell.text for cell in row.cells))
    return "\n".join(parts)


def parse_xlsx(path: str) -> str:
    wb = openpyxl.load_workbook(path, data_only=True)
    parts = []
    for sheet in wb.worksheets:
        parts.append(f"\n\n--- Sheet: {sheet.title} ---\n\n")
        for row in sheet.iter_rows(values_only=True):
            row_text = " | ".join(str(c) for c in row if c is not None)
            if row_text.strip():
                parts.append(row_text)
    return "\n".join(parts)


def parse_csv(path: str) -> str:
    df = pd.read_csv(path, on_bad_lines="skip", engine="python")
    return df.to_string(index=False)


def parse_txt(path: str) -> str:
    with open(path, "r", errors="ignore") as f:
        return f.read()


def parse_image(path: str) -> str:
    return ocr_image_file(path)


PARSERS = {
    "docx": parse_docx,
    "xlsx": parse_xlsx,
    "csv": parse_csv,
    "txt": parse_txt,
    "image": parse_image,
}


def parse_document(file_type: str, path: str) -> str:
    parser = PARSERS.get(file_type)
    if parser is None:
        raise ValueError(f"No parser available for file type: {file_type}")
    return parser(path)
