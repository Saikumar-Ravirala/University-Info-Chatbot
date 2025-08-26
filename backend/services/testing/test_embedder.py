# test_embedder.py
from backend.services.parser.pdf_parser import extract_text_from_pdf
from chunker import chunk_text
from embedder import get_embeddings

pdf_path = "sample-pdf-file.pdf"
text = extract_text_from_pdf(pdf_path)
chunks = chunk_text(text, chunk_size=500, overlap=50)
embeddings = get_embeddings(chunks)

print(f"Embeddings shape: {embeddings.shape}")
print(f"First vector (truncated): {embeddings[0][:10]}")
