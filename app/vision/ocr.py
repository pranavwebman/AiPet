"""Optical Character Recognition (OCR) module for AIPet."""

from pathlib import Path
from typing import Optional, List, Dict, Any
from app.vision.image_processor import ImageProcessor
from app.core.logger import logger

class OCRManager:
    """Handles text extraction from screenshots using pytesseract with graceful fallbacks."""

    @classmethod
    def extract_text(cls, image_path: Path) -> str:
        """
        Extract readable text from image. Returns empty string if pytesseract or Tesseract-OCR is missing.
        """
        if not image_path.exists():
            return ""

        try:
            import pytesseract
            enhanced_img = ImageProcessor.preprocess_for_ocr(image_path)
            if enhanced_img is None:
                return ""

            text = pytesseract.image_to_string(enhanced_img)
            cleaned = text.strip()
            logger.info(f"Extracted OCR text length: {len(cleaned)}")
            return cleaned

        except Exception as e:
            logger.warning(f"OCR extraction unavailable or failed (Tesseract binary might not be installed): {e}")
            return ""

    @classmethod
    def extract_data(cls, image_path: Path) -> List[Dict[str, Any]]:
        """
        Extract detailed OCR word bounding boxes if available.
        """
        if not image_path.exists():
            return []

        try:
            import pytesseract
            enhanced_img = ImageProcessor.preprocess_for_ocr(image_path)
            if enhanced_img is None:
                return []

            data = pytesseract.image_to_data(enhanced_img, output_type=pytesseract.Output.DICT)
            results = []
            n_boxes = len(data.get('text', []))
            for i in range(n_boxes):
                word = data['text'][i].strip()
                if word:
                    results.append({
                        "text": word,
                        "left": data['left'][i],
                        "top": data['top'][i],
                        "width": data['width'][i],
                        "height": data['height'][i],
                        "confidence": float(data['conf'][i])
                    })
            return results
        except Exception as e:
            logger.warning(f"OCR data extraction unavailable: {e}")
            return []
