"""Vision prompt packaging helper for multimodal LLM requests."""

import base64
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.vision.image_processor import ImageProcessor
from app.vision.active_window import ActiveWindowDetector
from app.vision.ocr import OCRManager
from app.core.config import get_config
from app.core.logger import logger

class VisionPromptBuilder:
    """Constructs multimodal vision user messages combining screenshots, active window context, and OCR."""

    @classmethod
    def build_vision_message(
        cls, prompt_text: str, image_path: Optional[Path] = None
    ) -> List[Dict[str, Any]]:
        """
        Builds user message content list conforming to OpenAI/NVIDIA NIM multimodal specifications.
        """
        config = get_config()
        content: List[Dict[str, Any]] = []

        # 1. Gather Active Window Context
        window_info = ActiveWindowDetector.get_active_window_info()
        context_str = (
            f"\n[Active Application Context: App='{window_info['app_name']}', "
            f"Title='{window_info['title']}', Bounds={window_info['bounds']}]"
        )

        # 2. Extract OCR text if enabled
        ocr_str = ""
        if config.get("enable_ocr", True) and image_path and image_path.exists():
            ocr_text = OCRManager.extract_text(image_path)
            if ocr_text:
                ocr_str = f"\n[OCR Text Detected on Screen:\n{ocr_text[:1000]}\n]"

        full_text = f"{prompt_text}\n{context_str}{ocr_str}"
        content.append({"type": "text", "text": full_text})

        # 3. Process Image and Base64 encode
        if image_path and image_path.exists():
            jpeg_bytes = ImageProcessor.optimize_for_vision_llm(image_path)
            if jpeg_bytes:
                b64_img = base64.b64encode(jpeg_bytes).decode("utf-8")
                image_url_payload = {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{b64_img}"
                    }
                }
                content.append(image_url_payload)
                logger.info("Successfully added screen capture image to vision request payload.")

        return content
