"""
OCR service — extracts text from scanned PDFs and images using Tesseract,
preserving basic paragraph/line structure.
"""
import io
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from app.config import get_settings

settings = get_settings()
pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


def ocr_image(image: Image.Image) -> str:
    # psm 6: assume a uniform block of text -> keeps structure reasonably intact
    config = "--psm 6"
    return pytesseract.image_to_string(image, config=config)


def ocr_pdf(path: str, dpi: int = 250) -> str:
    """
    Rasterize each page of a scanned PDF and run Tesseract on it.
    Returns text with page breaks preserved as '\\n\\n--- Page N ---\\n\\n'
    so downstream chunking/citation can reference page numbers.
    """
    doc = fitz.open(path)
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    full_text = []

    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        pix = page.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = ocr_image(img)
        full_text.append(f"\n\n--- Page {page_index + 1} ---\n\n{text}")

    doc.close()
    return "".join(full_text)


def ocr_image_file(path: str) -> str:
    img = Image.open(path)
    return ocr_image(img)
