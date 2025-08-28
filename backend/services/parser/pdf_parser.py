# backend/services/parser/pdf_parser.py
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
import io
import gc
from typing import List, Tuple, Optional
from langsmith import traceable
import logging

class PDFParser:
    """
    A class for parsing PDF files with native text extraction and OCR fallback.
    """
    
    def __init__(self, dpi: int = 150, y_threshold: int = 40, gpu: bool = False):
        """
        Initialize the PDF parser.
        
        Args:
            dpi: DPI for image rendering when OCR is needed
            y_threshold: Vertical proximity threshold for text block grouping
            gpu: Whether to use GPU for OCR (if available)
        """
        self.dpi = dpi
        self.y_threshold = y_threshold
        self.gpu = gpu
        self.logger = logging.getLogger(__name__)
        self._easyocr_reader = None
    
    def _get_ocr_reader(self):
        """Lazy loading of EasyOCR reader."""
        if self._easyocr_reader is None:
            try:
                import easyocr
                self._easyocr_reader = easyocr.Reader(['en'], gpu=self.gpu)
                self.logger.info("✅ Loaded EasyOCR reader")
            except ImportError:
                self.logger.error("❌ EasyOCR not installed. Please install with: pip install easyocr")
                raise
        return self._easyocr_reader
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extracts and concatenates text from all pages of a PDF.
        Cleans headers/footers and returns raw text.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        try:
            doc = fitz.open(file_path)
            full_text = ""

            for page in doc:
                text = page.get_text().strip()
                if text:
                    full_text += text + "\n"

            doc.close()
            gc.collect()
            return full_text.strip()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to extract text from PDF: {e}")
            raise
    
    def extract_text_blocks_from_image(self, image_bytes: bytes) -> List[dict]:
        """
        Performs OCR on image bytes using EasyOCR and returns text blocks with bounding boxes.
        
        Args:
            image_bytes: Image bytes to perform OCR on
            
        Returns:
            List of text blocks with bounding boxes and text content
        """
        try:
            reader = self._get_ocr_reader()
            
            img_np = np.frombuffer(image_bytes, np.uint8)
            img_cv = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
            
            if img_cv is None:
                self.logger.warning("⚠️ Failed to decode image bytes")
                return []
                
            img_gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
            _, thresh = cv2.threshold(img_gray, 180, 255, cv2.THRESH_BINARY_INV)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
            dilated = cv2.dilate(thresh, kernel, iterations=2)

            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            blocks = []
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if w > 50 and h > 50:
                    cropped = img_cv[y:y+h, x:x+w]
                    ocr_result = reader.readtext(cropped, detail=0)
                    if ocr_result:
                        blocks.append({
                            "bbox": (x, y, w, h),
                            "text": " ".join(ocr_result)
                        })

            blocks.sort(key=lambda b: b["bbox"][1])  # Sort top-to-bottom
            return blocks
            
        except Exception as e:
            self.logger.error(f"❌ OCR extraction failed: {e}")
            return []
        finally:
            # Clean up
            if 'img_cv' in locals():
                del img_cv
            if 'img_gray' in locals():
                del img_gray
            if 'thresh' in locals():
                del thresh
            if 'dilated' in locals():
                del dilated
            if 'contours' in locals():
                del contours
            gc.collect()
    
    def group_blocks_by_proximity(self, blocks: List[dict]) -> List[str]:
        """
        Groups OCR blocks based on vertical proximity.
        
        Args:
            blocks: List of text blocks with bounding boxes
            
        Returns:
            List of grouped text strings
        """
        if not blocks:
            return []
            
        grouped = []
        current_group = []

        for block in blocks:
            if not current_group:
                current_group.append(block)
                continue

            prev_y = current_group[-1]["bbox"][1]
            curr_y = block["bbox"][1]

            if abs(curr_y - prev_y) < self.y_threshold:
                current_group.append(block)
            else:
                grouped.append(current_group)
                current_group = [block]

        if current_group:
            grouped.append(current_group)

        return [" ".join(b["text"] for b in group) for group in grouped]
    
    @traceable
    def extract_text(self, pdf_path: str) -> str:
        """
        Extracts text from PDF using native text or OCR fallback.
        Returns concatenated text from all pages.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        try:
            page_texts = self.extract_pages_with_ocr(pdf_path)
            return "\n\n".join([text for _, text in page_texts])
        except Exception as e:
            self.logger.error(f"❌ Failed to extract text from PDF {pdf_path}: {e}")
            raise
    
    def extract_pages_with_ocr(self, pdf_path: str) -> List[Tuple[int, str]]:
        """
        Extracts text from each page of a PDF using native text or OCR fallback.
        Returns list of (page_number, text) tuples.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of (page_number, text) tuples
        """
        results = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num, page in enumerate(doc):
                page_text = page.get_text().strip()

                if not page_text:
                    self.logger.info(f"📄 Page {page_num + 1}: Using OCR fallback")
                    pix = page.get_pixmap(dpi=self.dpi)
                    img_bytes = pix.tobytes("png")
                    blocks = self.extract_text_blocks_from_image(img_bytes)
                    grouped_texts = self.group_blocks_by_proximity(blocks)
                    page_text = "\n".join(grouped_texts)
                    
                    del pix, img_bytes, blocks, grouped_texts
                else:
                    self.logger.info(f"📄 Page {page_num + 1}: Using native text extraction")

                results.append((page_num + 1, page_text))
                gc.collect()

            doc.close()
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to extract pages from PDF {pdf_path}: {e}")
            raise
        finally:
            gc.collect()
    
    def update_parameters(self, dpi: Optional[int] = None, y_threshold: Optional[int] = None) -> None:
        """
        Update parser parameters.
        
        Args:
            dpi: New DPI for image rendering
            y_threshold: New vertical proximity threshold
        """
        if dpi is not None:
            self.dpi = dpi
        if y_threshold is not None:
            self.y_threshold = y_threshold
        self.logger.info(f"🔄 Updated parameters: DPI={self.dpi}, Y-threshold={self.y_threshold}")
  