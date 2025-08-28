# backend/services/parser/img_parser.py
from typing import List, Tuple, Optional
import cv2
import numpy as np
import gc
import easyocr
import logging

class ImageParser:
    """
    A class for parsing image files and performing OCR.
    """
    
    def __init__(self, gpu: bool = False):
        """
        Initialize the Image parser.
        
        Args:
            gpu: Whether to use GPU for OCR (if available)
        """
        self.gpu = gpu
        self.logger = logging.getLogger(__name__)
        self._easyocr_reader = None
    
    def _get_ocr_reader(self):
        """Lazy loading of EasyOCR reader."""
        if self._easyocr_reader is None:
            try:
                self._easyocr_reader = easyocr.Reader(['en'], gpu=self.gpu)
                self.logger.info("✅ Loaded EasyOCR reader for image parsing")
            except ImportError:
                self.logger.error("❌ EasyOCR not installed. Please install with: pip install easyocr")
                raise
        return self._easyocr_reader
    
    def extract_text(self, image_path: str) -> str:
        """
        Extracts text from image file and returns as a single string.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text content
        """
        try:
            sections = self.extract_text_with_ocr(image_path)
            return "\n\n".join([text for _, text in sections])
        except Exception as e:
            self.logger.error(f"❌ Failed to extract text from image {image_path}: {e}")
            raise
    
    def extract_text_with_ocr(self, image_path: str) -> List[Tuple[int, str]]:
        """
        Performs OCR on an image file.
        Returns list of (section_number, text) tuples.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of (section_number, text) tuples
        """
        try:
            reader = self._get_ocr_reader()
            
            # Load image
            with open(image_path, "rb") as f:
                img_np = np.frombuffer(f.read(), np.uint8)
            
            img_cv = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
            
            if img_cv is None:
                self.logger.error("❌ Failed to decode image")
                return [(1, "")]
            
            # Perform OCR
            ocr_result = reader.readtext(img_cv, detail=0)
            grouped_text = "\n".join(ocr_result)
            
            return [(1, grouped_text)]
            
        except Exception as e:
            self.logger.error(f"❌ OCR failed for image {image_path}: {e}")
            return [(1, "")]
        finally:
            # Clean up
            if 'img_cv' in locals():
                del img_cv
            if 'img_np' in locals():
                del img_np
            gc.collect()
    
    def extract_text_with_confidence(self, image_path: str, confidence_threshold: float = 0.5) -> List[Tuple[str, float]]:
        """
        Extracts text from image with confidence scores.
        
        Args:
            image_path: Path to the image file
            confidence_threshold: Minimum confidence score to include text
            
        Returns:
            List of (text, confidence) tuples
        """
        try:
            reader = self._get_ocr_reader()
            
            # Load image
            with open(image_path, "rb") as f:
                img_np = np.frombuffer(f.read(), np.uint8)
            
            img_cv = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
            
            if img_cv is None:
                return []
            
            # Perform OCR with detailed results
            detailed_results = reader.readtext(img_cv)
            
            # Filter by confidence threshold
            filtered_results = [
                (text, confidence) 
                for (bbox, text, confidence) in detailed_results 
                if confidence >= confidence_threshold
            ]
            
            return filtered_results
            
        except Exception as e:
            self.logger.error(f"❌ Detailed OCR failed for image {image_path}: {e}")
            return []
        finally:
            gc.collect()
    
    def update_parameters(self, gpu: Optional[bool] = None) -> None:
        """
        Update parser parameters.
        
        Args:
            gpu: Whether to use GPU for OCR
        """
        if gpu is not None and gpu != self.gpu:
            self.gpu = gpu
            self._easyocr_reader = None  # Force reload with new GPU setting
            self.logger.info(f"🔄 Updated GPU setting: {gpu}")
     