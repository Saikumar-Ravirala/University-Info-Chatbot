# test_chunker.py
from chunker import chunk_text
from backend.services.parser.pdf_parser import extract_text_from_pdf

pdf_path = "sample-pdf-file.pdf"
text = extract_text_from_pdf(pdf_path)
chunks = chunk_text(text, chunk_size=500, overlap=50)

print(f"Total chunks: {len(chunks)}")
print(chunks[0])  # Preview first chunk
