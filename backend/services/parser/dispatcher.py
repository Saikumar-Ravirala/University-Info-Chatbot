from .pdf_parser import extract_pdf_with_region_ocr
from .doc_parser import extract_docx_text_with_ocr
from .img_parser import extract_text_from_image
from .txt_parser import extract_txt_text

def dispatch_parser(file_path: str) -> str:
    ext = file_path.lower().split('.')[-1]
    if ext == "pdf":
        return extract_pdf_with_region_ocr(file_path)
    elif ext in ["doc", "docx"]:
        return extract_docx_text_with_ocr(file_path)
    elif ext in ["jpg", "jpeg", "png"]:
        return extract_text_from_image(file_path)
    elif ext == "txt":
        return extract_txt_text(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
