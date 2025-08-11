# # chunker.py
# from typing import List

# def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
#     """
#     Splits text into overlapping chunks of specified size.
#     """
#     words = text.split()
#     chunks = []
#     start = 0

#     while start < len(words):
#         end = start + chunk_size
#         chunk = words[start:end]
#         chunks.append(" ".join(chunk))
#         start += chunk_size - overlap  # Slide window

#     return chunks

# chunker.py
from typing import List, Dict, Tuple

def chunk_text_with_metadata(pages: List[Tuple[int, str]], source_file: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
    """
    Splits each page's text into chunks and tags each with metadata.
    """
    all_chunks = []

    for page_num, text in pages:
        words = text.split()
        start = 0
        chunk_index = 0

        while start < len(words):
            end = start + chunk_size
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            all_chunks.append({
                "text": chunk_text,
                "page": page_num,
                "source": source_file,
                "chunk_id": f"{source_file}_p{page_num}_c{chunk_index}"
            })

            start += chunk_size - overlap
            chunk_index += 1

    return all_chunks
