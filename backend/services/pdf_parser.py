# pdf_parser.py
import fitz  # PyMuPDF
from typing import List, Tuple

#imports for easyocr
import cv2
import numpy as np
import easyocr
from PIL import Image
import io
# import json

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts and concatenates text from all pages of a PDF.
    Cleans headers/footers and returns raw text.
    """
    doc = fitz.open(file_path)
    full_text = ""

    for page in doc:
        text = page.get_text()
        # Optional: Clean headers/footers or whitespace
        cleaned_text = text.strip()
        full_text += cleaned_text + "\n"

    doc.close()
    return full_text

############################################################################################################

# Initialize EasyOCR
# reader = easyocr.Reader(['en'])

# def extract_text_blocks_from_image(image_bytes):
#     # Convert image bytes to OpenCV format
#     image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
#     img_cv = np.array(image)
#     img_gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)

#     # Threshold to separate text from background
#     _, thresh = cv2.threshold(img_gray, 180, 255, cv2.THRESH_BINARY_INV)

#     # Dilate to merge text lines within a block
#     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
#     dilated = cv2.dilate(thresh, kernel, iterations=2)

#     # Find contours (possible text regions)
#     contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     extracted_blocks = []
#     for cnt in contours:
#         x, y, w, h = cv2.boundingRect(cnt)
#         if w > 50 and h > 50:  # filter out noise
#             cropped = img_cv[y:y+h, x:x+w]
#             ocr_result = reader.readtext(cropped, detail=0)
#             if ocr_result:
#                 extracted_blocks.append({
#                     "bbox": (x, y, w, h),
#                     "text": " ".join(ocr_result)
#                 })

#     # Sort blocks top-to-bottom, left-to-right
#     extracted_blocks.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))
#     return extracted_blocks


# def extract_pdf_with_region_ocr(pdf_path):
#     doc = fitz.open(pdf_path)
#     results = []
#     for page_num, page in enumerate(doc):
#         page_text = page.get_text().strip()
#         if not page_text:
#             pix = page.get_pixmap(dpi=300)
#             img_bytes = pix.tobytes("png")
#             blocks = extract_text_blocks_from_image(img_bytes)
#             page_text = "\n".join(b["text"] for b in blocks)
#         results.append((page_num + 1, page_text))
#     return results

reader = easyocr.Reader(['en'])

def extract_text_blocks_from_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_cv = np.array(image)
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

    # Sort top-to-bottom
    blocks.sort(key=lambda b: b["bbox"][1])
    return blocks

def group_blocks_by_proximity(blocks, y_threshold=40):
    grouped = []
    current_group = []

    for i, block in enumerate(blocks):
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

def extract_pdf_with_region_ocr(pdf_path):
    doc = fitz.open(pdf_path)
    results = []

    for page_num, page in enumerate(doc):
        page_text = page.get_text().strip()
        if not page_text:
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")
            blocks = extract_text_blocks_from_image(img_bytes)
            grouped_texts = group_blocks_by_proximity(blocks)
            page_text = "\n".join(grouped_texts)

        results.append((page_num + 1, page_text))
    return results
    
############################################################################################################
