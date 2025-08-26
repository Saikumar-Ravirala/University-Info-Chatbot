from typing import List, Tuple
import cv2, numpy as np, gc
import easyocr

def extract_text_from_image(image_path: str) -> List[Tuple[int, str]]:
    """
    Lazily loads image from disk and performs OCR.
    Returns list of (section_number, text) tuples.
    """
    reader = easyocr.Reader(['en'], gpu=False)

    # Lazy load: decode only when needed
    def load_image(path: str):
        with open(path, "rb") as f:
            return np.frombuffer(f.read(), np.uint8)

    img_np = load_image(image_path)
    img_cv = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

    ocr_result = reader.readtext(img_cv, detail=0)
    grouped_text = "\n".join(ocr_result)

    del reader, img_cv, img_np
    gc.collect()
    return [(1, grouped_text)]
