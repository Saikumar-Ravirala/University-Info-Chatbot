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

