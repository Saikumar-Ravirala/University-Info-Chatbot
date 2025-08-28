# backend/services/parser/txt_parser.py
from typing import List, Tuple, Optional
import logging

class TXTParser:
    """
    A class for parsing plain text files.
    """
    
    def __init__(self, encoding: str = "utf-8", chunk_size: int = 1000):
        """
        Initialize the TXT parser.
        
        Args:
            encoding: Text file encoding
            chunk_size: Size of text chunks for processing
        """
        self.encoding = encoding
        self.chunk_size = chunk_size
        self.logger = logging.getLogger(__name__)
    
    def extract_text(self, txt_path: str) -> str:
        """
        Extracts text from TXT file and returns as a single string.
        
        Args:
            txt_path: Path to the TXT file
            
        Returns:
            Extracted text content
        """
        try:
            with open(txt_path, "r", encoding=self.encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            self.logger.warning(f"⚠️ UTF-8 decoding failed for {txt_path}, trying latin-1")
            try:
                with open(txt_path, "r", encoding="latin-1") as f:
                    return f.read()
            except Exception as e:
                self.logger.error(f"❌ Failed to read TXT file {txt_path}: {e}")
                raise
        except Exception as e:
            self.logger.error(f"❌ Failed to read TXT file {txt_path}: {e}")
            raise
    
    def extract_text_chunks(self, txt_path: str) -> List[Tuple[int, str]]:
        """
        Reads a plain text file and returns line-wise chunks.
        
        Args:
            txt_path: Path to the TXT file
            
        Returns:
            List of (line_number, text) tuples
        """
        results = []
        try:
            with open(txt_path, "r", encoding=self.encoding) as f:
                for i, line in enumerate(f):
                    text = line.strip()
                    if text:
                        results.append((i + 1, text))
            return results
        except UnicodeDecodeError:
            self.logger.warning(f"⚠️ UTF-8 decoding failed for {txt_path}, trying latin-1")
            try:
                with open(txt_path, "r", encoding="latin-1") as f:
                    for i, line in enumerate(f):
                        text = line.strip()
                        if text:
                            results.append((i + 1, text))
                return results
            except Exception as e:
                self.logger.error(f"❌ Failed to read TXT file {txt_path}: {e}")
                raise
        except Exception as e:
            self.logger.error(f"❌ Failed to read TXT file {txt_path}: {e}")
            raise
    
    def extract_large_text_chunks(self, txt_path: str) -> List[Tuple[int, str]]:
        """
        Reads a large text file and returns chunks of specified size.
        
        Args:
            txt_path: Path to the TXT file
            
        Returns:
            List of (chunk_number, text) tuples
        """
        results = []
        chunk_number = 1
        current_chunk = []
        current_size = 0
        
        try:
            with open(txt_path, "r", encoding=self.encoding) as f:
                for line in f:
                    stripped_line = line.strip()
                    if stripped_line:
                        current_chunk.append(stripped_line)
                        current_size += len(stripped_line)
                        
                        if current_size >= self.chunk_size:
                            results.append((chunk_number, " ".join(current_chunk)))
                            chunk_number += 1
                            current_chunk = []
                            current_size = 0
            
            # Add the last chunk if it has content
            if current_chunk:
                results.append((chunk_number, " ".join(current_chunk)))
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to read large TXT file {txt_path}: {e}")
            raise
    
    def update_parameters(self, encoding: Optional[str] = None, chunk_size: Optional[int] = None) -> None:
        """
        Update parser parameters.
        
        Args:
            encoding: New text encoding
            chunk_size: New chunk size
        """
        if encoding is not None:
            self.encoding = encoding
        if chunk_size is not None:
            self.chunk_size = chunk_size
        self.logger.info(f"🔄 Updated parameters: encoding={self.encoding}, chunk_size={self.chunk_size}")
        
# from typing import List, Tuple

# def extract_txt_text(txt_path: str) -> List[Tuple[int, str]]:
#     """
#     Reads a plain text file and returns line-wise chunks.
#     """
#     results = []
#     with open(txt_path, "r", encoding="utf-8") as f:
#         for i, line in enumerate(f):
#             text = line.strip()
#             if text:
#                 results.append((i + 1, text))
#     return results
