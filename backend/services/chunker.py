# backend/services/chunker.py
from typing import List, Dict, Tuple

class TextChunker:
    """
    A class for splitting text into chunks with metadata tagging.
    """
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        Initialize the TextChunker with default chunking parameters.
        
        Args:
            chunk_size: Number of words per chunk (default: 500)
            overlap: Number of overlapping words between chunks (default: 50)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text_with_metadata(self, pages: List[Tuple[int, str]], source_file: str) -> List[Dict]:
        """
        Splits each page's text into chunks and tags each with metadata.
        
        Args:
            pages: List of tuples containing (page_number, text)
            source_file: Source file identifier for metadata
            
        Returns:
            List of dictionaries containing chunk data and metadata
        """
        all_chunks = []

        for page_num, text in pages:
            words = text.split()
            start = 0
            chunk_index = 0

            while start < len(words):
                end = start + self.chunk_size
                chunk_words = words[start:end]
                chunk_text = " ".join(chunk_words)

                all_chunks.append({
                    "text": chunk_text,
                    "page": page_num,
                    "source": source_file,
                    "chunk_id": f"{source_file}_p{page_num}_c{chunk_index}"
                })

                start += self.chunk_size - self.overlap
                chunk_index += 1

        return all_chunks
    
    def update_chunking_parameters(self, chunk_size: int = None, overlap: int = None):
        """
        Update the chunking parameters.
        
        Args:
            chunk_size: New chunk size (if provided)
            overlap: New overlap size (if provided)
        """
        if chunk_size is not None:
            self.chunk_size = chunk_size
        if overlap is not None:
            self.overlap = overlap
            
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

# backend/services/chunker.py
# from typing import List, Dict, Tuple

# def chunk_text_with_metadata(pages: List[Tuple[int, str]], source_file: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
#     """
#     Splits each page's text into chunks and tags each with metadata.
#     """
#     all_chunks = []

#     for page_num, text in pages:
#         words = text.split()
#         start = 0
#         chunk_index = 0

#         while start < len(words):
#             end = start + chunk_size
#             chunk_words = words[start:end]
#             chunk_text = " ".join(chunk_words)

#             all_chunks.append({
#                 "text": chunk_text,
#                 "page": page_num,
#                 "source": source_file,
#                 "chunk_id": f"{source_file}_p{page_num}_c{chunk_index}"
#             })

#             start += chunk_size - overlap
#             chunk_index += 1

#     return all_chunks
