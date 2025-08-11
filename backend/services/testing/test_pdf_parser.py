# test_pdf_parser.py
from services.pdf_parser import extract_text_by_page

pdf_path = "backend\\temp\\sample brochure 2.pdf"  # Replace with your test file
# text = extract_text_from_pdf(pdf_path)
text = extract_text_by_page(pdf_path)
print(text[:1000])  # Print first 1000 characters for preview
