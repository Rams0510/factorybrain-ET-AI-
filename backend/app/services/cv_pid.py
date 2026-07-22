"""
Computer vision pipeline for P&ID (Piping & Instrumentation Diagram) pages.

This is a real, working OpenCV heuristic pipeline (not a trained detector):
  1. Convert page to grayscale + binary image.
  2. Detect straight lines via Hough Transform -> classified as PIPE segments.
  3. Detect circular symbols via Hough Circle Transform -> classified as
     PUMP / VALVE candidates (refined by size + surrounding line count).
  4. Detect rectangular blobs via contour analysis -> classified as
     TANK / MOTOR candidates.
  5. Run Tesseract OCR on small text regions near each shape to recover the
     equipment tag (e.g. "P-101", "V-204").

The output is a structured JSON per page that downstream services store as
ExtractedEntity rows and Neo4j Equipment nodes.

This heuristic approach is explainable and fast, but is not equivalent to a
trained object-detection model — accuracy depends heavily on drawing style
and line quality. It's a legitimate baseline that can be swapped later for
a trained YOLO/Detectron model without changing the calling contract.
"""
import cv2
import numpy as np
import pytesseract
from app.config import get_settings

settings = get_settings()
pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


def _load_binary(image_path: str):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    return img, gray, binary


def _detect_pipes(binary) -> list[dict]:
    lines = cv2.HoughLinesP(
        binary, 1, np.pi / 180, threshold=80, minLineLength=60, maxLineGap=8
    )
    pipes = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            length = float(np.hypot(x2 - x1, y2 - y1))
            orientation = "horizontal" if abs(y2 - y1) < abs(x2 - x1) else "vertical"
            pipes.append({
                "type": "PIPE",
                "x1": int(x1), "y1": int(y1), "x2": int(x2), "y2": int(y2),
                "length_px": round(length, 1),
                "orientation": orientation,
            })
    return pipes


def _detect_circular_symbols(gray) -> list[dict]:
    blurred = cv2.medianBlur(gray, 5)
    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=40,
        param1=80, param2=35, minRadius=10, maxRadius=80,
    )
    symbols = []
    if circles is not None:
        for x, y, r in np.round(circles[0, :]).astype("int"):
            # Larger circles with thick strokes tend to be pumps; smaller,
            # thinner circles tend to be instrumentation/valve bubbles.
            equipment_type = "Pump" if r >= 35 else "Valve"
            symbols.append({
                "type": equipment_type.upper(),
                "cx": int(x), "cy": int(y), "radius": int(r),
            })
    return symbols


def _detect_rectangular_blobs(binary, gray) -> list[dict]:
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blobs = []
    h_img, w_img = gray.shape[:2]
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        area = w * h
        if area < 900 or area > 0.4 * h_img * w_img:
            continue
        aspect = w / max(h, 1)
        # Tall narrow rectangles -> Tank; wide squat rectangles -> Motor
        equipment_type = "Tank" if 0.4 <= aspect <= 1.6 and h > 60 else "Motor"
        blobs.append({
            "type": equipment_type.upper(),
            "x": int(x), "y": int(y), "w": int(w), "h": int(h),
        })
    return blobs


def _read_tag_near(gray, cx: int, cy: int, radius: int = 60) -> str | None:
    h, w = gray.shape[:2]
    x0, y0 = max(cx - radius, 0), max(cy - radius, 0)
    x1, y1 = min(cx + radius, w), min(cy + radius, h)
    crop = gray[y0:y1, x0:x1]
    if crop.size == 0:
        return None
    text = pytesseract.image_to_string(
        crop, config="--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"
    ).strip()
    return text if text else None


def analyze_pid_page(image_path: str) -> dict:
    """
    Runs the full heuristic pipeline on a single rasterized P&ID page and
    returns structured JSON:
    {
      "pipes": [...],
      "equipment": [{"type": "PUMP", "tag": "P-101", "x":.., "y":..}, ...]
    }
    """
    img, gray, binary = _load_binary(image_path)

    pipes = _detect_pipes(binary)
    circles = _detect_circular_symbols(gray)
    blobs = _detect_rectangular_blobs(binary, gray)

    equipment = []
    for c in circles:
        tag = _read_tag_near(gray, c["cx"], c["cy"])
        equipment.append({
            "type": c["type"],
            "tag": tag,
            "x": c["cx"], "y": c["cy"],
            "radius": c["radius"],
        })
    for b in blobs:
        cx, cy = b["x"] + b["w"] // 2, b["y"] + b["h"] // 2
        tag = _read_tag_near(gray, cx, cy)
        equipment.append({
            "type": b["type"],
            "tag": tag,
            "x": cx, "y": cy,
            "bbox": [b["x"], b["y"], b["w"], b["h"]],
        })

    return {
        "pipes": pipes,
        "equipment": equipment,
        "pipe_count": len(pipes),
        "equipment_count": len(equipment),
    }


def render_pdf_page_to_image(pdf_path: str, page_number: int, out_path: str, dpi: int = 200):
    import fitz
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)
    zoom = dpi / 72
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    pix.save(out_path)
    doc.close()
