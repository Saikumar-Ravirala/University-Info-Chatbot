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


#adding metadata extraction
def extract_text_by_page(file_path: str) -> List[Tuple[int, str]]:
    """
    Extracts text from each page of a PDF and returns (page_number, text) tuples.
    """
    doc = fitz.open(file_path)
    page_texts = []

    for i, page in enumerate(doc):
        text = page.get_text().strip()
        page_texts.append((i + 1, text))  # Page numbers start at 1

    doc.close()
    return page_texts


############################################################################################################
#pytesseract
#adding ocr with text extraction
import pytesseract
from PIL import Image
import io
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

def extract_text_and_images_by_page(pdf_path: str) -> List[Tuple[int, str]]:
    doc = fitz.open(pdf_path)
    results = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)

        # Step 1: Extract native text
        text = page.get_text().strip()

        # Step 2: Extract embedded images
        image_texts = []
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))

            # Apply OCR only to the image
            ocr_text = pytesseract.image_to_string(image)
            if ocr_text.strip():
                image_texts.append(ocr_text.strip())

        # Step 3: Combine text + OCR
        combined_text = text + "\n" + "\n".join(f"[OCR] {t}" for t in image_texts)
        results.append((page_num + 1, combined_text))

    return results  # List of (page_number, combined_text)

############################################################################################################


############################################################################################################
# import easyocr
# import numpy as np
# from PIL import Image


# reader = easyocr.Reader(['en'], gpu=False)

# def ocr_image_preserve_layout(pil_image, y_threshold=10):
#     results = reader.readtext(np.array(pil_image), detail=1, paragraph=False)
#     # Each result: [ [ [x1,y1], [x2,y2], [x3,y3], [x4,y4] ], text, confidence ]
    
#     # Convert to (y, x, text)
#     data = []
#     for (bbox, text, conf) in results:
#         x_coords = [p[0] for p in bbox]
#         y_coords = [p[1] for p in bbox]
#         avg_x = sum(x_coords) / 4
#         avg_y = sum(y_coords) / 4
#         data.append((avg_y, avg_x, text))
    
#     # Sort by y, then x
#     data.sort(key=lambda r: (r[0], r[1]))
    
#     # Group into lines based on y distance
#     lines = []
#     current_line = []
#     current_y = None
    
#     for (y, x, text) in data:
#         if current_y is None:
#             current_y = y
#         if abs(y - current_y) > y_threshold:
#             # new line
#             lines.append(" ".join(current_line))
#             current_line = [text]
#             current_y = y
#         else:
#             current_line.append(text)
#     if current_line:
#         lines.append(" ".join(current_line))
    
#     return "\n".join(lines)

def extract_text_and_images_by_page_with_easyOCR(pdf_path):
    doc = fitz.open(pdf_path)
    results = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)

        # Native text
        text = page.get_text().strip()

        # OCR images
        image_texts = []
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))

            ocr_text = ocr_image_preserve_layout(image)
            if ocr_text.strip():
                image_texts.append(ocr_text)

        combined_text = text + "\n" + "\n".join(f"[OCR] {t}" for t in image_texts)
        results.append((page_num + 1, combined_text))
    return results

############################################################################################################

# import fitz  # PyMuPDF
# import easyocr
# import numpy as np
# from PIL import Image
# import io

# # Initialize EasyOCR reader once
# reader = easyocr.Reader(['en'], gpu=False)

# def ocr_image_preserve_layout(pil_image, y_threshold=10):
#     results = reader.readtext(np.array(pil_image), detail=1, paragraph=False)
#     data = []
#     for (bbox, text, conf) in results:
#         x_coords = [p[0] for p in bbox]
#         y_coords = [p[1] for p in bbox]
#         avg_x = sum(x_coords) / 4
#         avg_y = sum(y_coords) / 4
#         data.append((avg_y, avg_x, text))
#     data.sort(key=lambda r: (r[0], r[1]))
    
#     lines = []
#     current_line = []
#     current_y = None
#     for (y, x, text) in data:
#         if current_y is None:
#             current_y = y
#         if abs(y - current_y) > y_threshold:
#             lines.append(" ".join(current_line))
#             current_line = [text]
#             current_y = y
#         else:
#             current_line.append(text)
#     if current_line:
#         lines.append(" ".join(current_line))
    
#     return "\n".join(lines)

def extract_text_with_hybrid_approach(pdf_path, text_threshold=20):
    doc = fitz.open(pdf_path)
    results = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        native_text = page.get_text().strip()

        if len(native_text) > text_threshold:
            # Page already has extractable text → OCR only on images
            image_texts = []
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes))
                ocr_text = ocr_image_preserve_layout(image)
                if ocr_text.strip():
                    image_texts.append(ocr_text)
            combined_text = native_text + ("\n" + "\n".join(f"[OCR] {t}" for t in image_texts) if image_texts else "")
        
        else:
            # Page is likely scanned → Convert whole page to image & OCR
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            combined_text = ocr_image_preserve_layout(img)

        results.append((page_num + 1, combined_text))
    
    return results

# # Example usage:
# pdf_path = "university_info.pdf"
# data = extract_text_with_hybrid_approach(pdf_path)

# for page_num, text in data:
#     print(f"\n--- Page {page_num} ---\n{text}")

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

############################################################################################################

# parser.py
#adding paddleocr with text extraction

#imports for paddleocr
# import fitz  # PyMuPDF
# import cv2
# import numpy as np
#from paddleocr import PaddleOCR
# from PIL import Image
# import io
# Initialize PaddleOCR (English, lightweight model)
# ocr = PaddleOCR(use_angle_cls=True, lang='en')

# def extract_text_blocks_from_image_paddleocr(image_bytes, page_num, source):
#     image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
#     img_cv = np.array(image)
#     img_gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)

#     _, thresh = cv2.threshold(img_gray, 180, 255, cv2.THRESH_BINARY_INV)
#     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
#     dilated = cv2.dilate(thresh, kernel, iterations=2)

#     contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     extracted_blocks = []
#     block_id = 0

#     for cnt in contours:
#         x, y, w, h = cv2.boundingRect(cnt)
#         if w > 50 and h > 50:
#             cropped = img_cv[y:y+h, x:x+w]

#             try:
#                 ocr_result = ocr.ocr(cropped)
#             except Exception as e:
#                 print(f"⚠️ OCR failed at {(x, y, w, h)}: {e}")
#                 continue

#             if not ocr_result or not isinstance(ocr_result[0], list):
#                 print(f"⚠️ No valid OCR output for block at {(x, y, w, h)}")
#                 continue

#             lines, confidences = [], []

#             for line in ocr_result[0]:
#                 if isinstance(line, list) and len(line) == 2:
#                     box, text_conf = line
#                     if isinstance(text_conf, list) and len(text_conf) == 2:
#                         txt, conf = text_conf
#                         lines.append(txt)
#                         confidences.append(conf)
#                     else:
#                         print(f"⚠️ Skipped malformed OCR line: {line} (unexpected text/conf format)")
#                 else:
#                     print(f"⚠️ Skipped malformed OCR line: {line} (unexpected structure)")

#             if lines:
#                 avg_conf = float(np.mean(confidences)) if confidences else 0.0
#                 if avg_conf < 0.4:
#                     print(f"⚠️ Low confidence block at {(x, y, w, h)}: {avg_conf:.2f}, skipping.")
#                     continue

#                 block_id += 1
#                 extracted_blocks.append({
#                     "page": page_num,
#                     "block_id": block_id,
#                     "bbox": (x, y, w, h),
#                     "text": " ".join(lines),
#                     "confidence": avg_conf,
#                     "source": source,
#                     "type": "ocr_text"
#                 })

#     extracted_blocks.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))
#     return extracted_blocks

# def extract_pdf_with_region_paddleocr(pdf_path, source=None):
#     doc = fitz.open(pdf_path)
#     results = []

#     for page_num, page in enumerate(doc):
#         page_text = page.get_text().strip()

#         if not page_text:
#             pix = page.get_pixmap(dpi=300)
#             img_bytes = pix.tobytes("png")
#             blocks = extract_text_blocks_from_image_paddleocr(img_bytes, page_num + 1, source or pdf_path)
#             results.extend(blocks)
#         else:
#             results.append({
#                 "page": page_num + 1,
#                 "block_id": 1,
#                 "bbox": None,
#                 "text": page_text,
#                 "confidence": 1.0,
#                 "source": source or pdf_path,
#                 "type": "native_text"
#             })

#     return results
############################################################################################################