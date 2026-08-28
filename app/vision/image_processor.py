"""Image processing utilities for AIPet screen captures and OCR preprocessing."""

import io
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageEnhance
from app.core.logger import logger

class ImageProcessor:
    """Provides methods to optimize image formats and sizes for AI vision models."""

    @classmethod
    def optimize_for_vision_llm(
        cls, image_path: Path, max_dimension: int = 1280, quality: int = 85
    ) -> Optional[bytes]:
        """
        Compress and resize image if necessary to fit token/payload constraints.
        Returns JPEG bytes.
        """
        if not image_path.exists():
            logger.error(f"Image path does not exist: {image_path}")
            return None

        try:
            with Image.open(image_path) as img:
                img = img.convert("RGB")
                w, h = img.size

                if max(w, h) > max_dimension:
                    if w > h:
                        new_w = max_dimension
                        new_h = int(h * (max_dimension / w))
                    else:
                        new_h = max_dimension
                        new_w = int(w * (max_dimension / h))
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    logger.debug(f"Resized screenshot from {w}x{h} to {new_w}x{new_h}")

                output = io.BytesIO()
                img.save(output, format="JPEG", quality=quality)
                return output.getvalue()

        except Exception as e:
            logger.error(f"Error optimizing image for vision LLM: {e}")
            return None

    @classmethod
    def preprocess_for_ocr(cls, image_path: Path) -> Optional[Image.Image]:
        """Enhance image contrast and convert to grayscale for OCR accuracy."""
        if not image_path.exists():
            return None

        try:
            with Image.open(image_path) as img:
                gray = img.convert("L")
                enhancer = ImageEnhance.Contrast(gray)
                enhanced = enhancer.enhance(2.0)
                return enhanced
        except Exception as e:
            logger.error(f"Error preprocessing image for OCR: {e}")
            return None
