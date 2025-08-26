from typing import List, Tuple
from docx import Document
from PIL import Image
import easyocr, io, gc
import numpy as np

def extract_docx_text_with_ocr(docx_path: str) -> List[Tuple[int, str]]:
    """
    Lazily extracts text and OCR from a .docx file.
    Returns list of (section_number, text) tuples.
    """
    doc = Document(docx_path)
    reader = easyocr.Reader(['en'], gpu=False)
    results = []
    section_num = 1

    # Stream paragraphs
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            results.append((section_num, text))
            section_num += 1

    # Stream embedded images
    for rel in doc.part._rels:
        target = doc.part._rels[rel].target_ref
        if target.lower().endswith((".png", ".jpg", ".jpeg")):
            try:
                # Lazy load image blob
                image_blob = doc.part.related_parts[target].blob
                image_stream = io.BytesIO(image_blob)

                # Decode only when needed
                image = Image.open(image_stream).convert("RGB")
                image_np = np.array(image)

                ocr_result = reader.readtext(image_np, detail=0)
                if ocr_result:
                    results.append((section_num, "\n".join(ocr_result)))
                    section_num += 1

                del image, image_np, image_stream, image_blob
                gc.collect()
            except Exception as e:
                print(f"Image OCR failed: {e}")

    del reader
    gc.collect()
    return results
