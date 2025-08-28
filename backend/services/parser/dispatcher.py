# backend/services/parser/dispatcher.py
from typing import Dict, Callable, Optional
import logging
from .pdf_parser import PDFParser
from .doc_parser import DOCXParser
from .img_parser import ImageParser
from .txt_parser import TXTParser

class ParserDispatcher:
    """
    A class that dispatches file parsing to the appropriate parser based on file extension.
    """
    
    def __init__(self):
        """
        Initialize the parser dispatcher with available parsers.
        """
        self.parsers: Dict[str, Callable] = {}
        self.logger = logging.getLogger(__name__)
        self._initialize_parsers()
    
    def _initialize_parsers(self) -> None:
        """Initialize all available parsers."""
        self.parsers = {
            "pdf": PDFParser().extract_text,
            "doc": DOCXParser().extract_text,
            "docx": DOCXParser().extract_text,
            "jpg": ImageParser().extract_text,
            "jpeg": ImageParser().extract_text,
            "png": ImageParser().extract_text,
            "txt": TXTParser().extract_text
        }
    
    def get_supported_extensions(self) -> list:
        """
        Get list of supported file extensions.
        
        Returns:
            List of supported file extensions
        """
        return list(self.parsers.keys())
    
    def dispatch_parser(self, file_path: str) -> str:
        """
        Dispatch file parsing to the appropriate parser based on file extension.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Extracted text content
            
        Raises:
            ValueError: If file type is not supported
        """
        ext = file_path.lower().split('.')[-1]
        
        if ext in self.parsers:
            self.logger.info(f"🔄 Dispatching {ext.upper()} file to parser: {file_path}")
            return self.parsers[ext](file_path)
        else:
            error_msg = f"Unsupported file type: {ext}"
            self.logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
    
    def register_parser(self, extension: str, parser_func: Callable) -> None:
        """
        Register a new parser for a file extension.
        
        Args:
            extension: File extension (without dot)
            parser_func: Parser function that takes file_path and returns text
        """
        self.parsers[extension.lower()] = parser_func
        self.logger.info(f"✅ Registered parser for .{extension} files")
    
    def unregister_parser(self, extension: str) -> None:
        """
        Unregister a parser for a file extension.
        
        Args:
            extension: File extension to unregister
        """
        if extension.lower() in self.parsers:
            del self.parsers[extension.lower()]
            self.logger.info(f"🗑️ Unregistered parser for .{extension} files")

            