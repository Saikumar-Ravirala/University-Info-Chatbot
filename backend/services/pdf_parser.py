# pdf_parser.py
import fitz  # PyMuPDF
from typing import List, Tuple

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

