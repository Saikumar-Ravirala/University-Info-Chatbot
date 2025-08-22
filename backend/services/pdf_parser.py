import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
import io
import gc
from typing import List, Tuple

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts and concatenates text from all pages of a PDF.
    Cleans headers/footers and returns raw text.
    """
    doc = fitz.open(file_path)
    full_text = ""

    for page in doc:
        text = page.get_text().strip()
        full_text += text + "\n"

    doc.close()
    gc.collect()
    return full_text

def extract_text_blocks_from_image(image_bytes: bytes) -> List[dict]:
    """
    Performs OCR on image bytes using EasyOCR and returns text blocks with bounding boxes.
    """
    import easyocr
    reader = easyocr.Reader(['en'], gpu=False)

    img_np = np.frombuffer(image_bytes, np.uint8)
    img_cv = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
    img_gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)

    _, thresh = cv2.threshold(img_gray, 180, 255, cv2.THRESH_BINARY_INV)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
    dilated = cv2.dilate(thresh, kernel, iterations=2)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    blocks = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 50 and h > 50:
            cropped = img_cv[y:y+h, x:x+w]
            ocr_result = reader.readtext(cropped, detail=0)
            if ocr_result:
                blocks.append({
                    "bbox": (x, y, w, h),
                    "text": " ".join(ocr_result)
                })

    blocks.sort(key=lambda b: b["bbox"][1])  # Sort top-to-bottom
    del reader, img_cv, img_gray, thresh, dilated, contours
    gc.collect()
    return blocks

def group_blocks_by_proximity(blocks: List[dict], y_threshold: int = 40) -> List[str]:
    """
    Groups OCR blocks based on vertical proximity.
    """
    grouped = []
    current_group = []

    for block in blocks:
        if not current_group:
            current_group.append(block)
            continue

        prev_y = current_group[-1]["bbox"][1]
        curr_y = block["bbox"][1]

        if abs(curr_y - prev_y) < y_threshold:
            current_group.append(block)
        else:
            grouped.append(current_group)
            current_group = [block]

    if current_group:
        grouped.append(current_group)

    return [" ".join(b["text"] for b in group) for group in grouped]

def extract_pdf_with_region_ocr(pdf_path: str) -> List[Tuple[int, str]]:
    """
    Extracts text from each page of a PDF using native text or OCR fallback.
    Returns list of (page_number, text) tuples.
    """
    doc = fitz.open(pdf_path)
    results = []

    for page_num, page in enumerate(doc):
        page_text = page.get_text().strip()

        if not page_text:
            pix = page.get_pixmap(dpi=150)  # Lower DPI for memory savings
            img_bytes = pix.tobytes("png")
            blocks = extract_text_blocks_from_image(img_bytes)
            grouped_texts = group_blocks_by_proximity(blocks)
            page_text = "\n".join(grouped_texts)

            del pix, img_bytes, blocks, grouped_texts
            gc.collect()

        results.append((page_num + 1, page_text))

    doc.close()
    gc.collect()
    return results
