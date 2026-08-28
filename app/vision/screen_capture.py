"""Screen capture utilities for AIPet using MSS or PySide6 QScreen fallback."""

import sys
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from PIL import Image
from app.core.config import get_cache_dir
from app.core.logger import logger
from app.core.exceptions import VisionError

class ScreenCapturer:
    """Handles full screen and region desktop captures safely."""

    @classmethod
    def capture_full_screen(cls, monitor_index: int = 0) -> Optional[Path]:
        """Capture the desktop and save to a temporary file in cache directory."""
        cache_dir = get_cache_dir()
        file_path = cache_dir / "screen_capture.png"

        try:
            import mss
            with mss.mss() as sct:
                # mss monitors: index 0 is all monitors combined, 1 is primary monitor
                m_idx = monitor_index + 1 if len(sct.monitors) > 1 else 0
                if m_idx >= len(sct.monitors):
                    m_idx = 0
                monitor = sct.monitors[m_idx]
                sct_img = sct.grab(monitor)

                # Convert to PIL Image and save
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                img.save(file_path, "PNG")
                logger.info(f"Captured full screen via MSS: {file_path}")
                return file_path
        except Exception as e:
            logger.warning(f"MSS screen capture failed, attempting QScreen fallback: {e}")
            return cls._capture_via_qscreen(file_path)

    @classmethod
    def capture_region(cls, bbox: Tuple[int, int, int, int]) -> Optional[Path]:
        """
        Capture specific bounding box region (left, top, width, height).
        """
        left, top, width, height = bbox
        if width <= 0 or height <= 0:
            logger.error(f"Invalid region dimensions: {bbox}")
            return None

        cache_dir = get_cache_dir()
        file_path = cache_dir / "window_capture.png"

        try:
            import mss
            with mss.mss() as sct:
                region = {"left": left, "top": top, "width": width, "height": height}
                sct_img = sct.grab(region)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                img.save(file_path, "PNG")
                logger.info(f"Captured region {bbox} via MSS: {file_path}")
                return file_path
        except Exception as e:
            logger.warning(f"MSS region capture failed: {e}")
            # Fallback to cropping full screenshot
            full_path = cls.capture_full_screen()
            if full_path and full_path.exists():
                try:
                    img = Image.open(full_path)
                    cropped = img.crop((left, top, left + width, top + height))
                    cropped.save(file_path, "PNG")
                    return file_path
                except Exception as crop_err:
                    logger.error(f"Failed to crop full screenshot: {crop_err}")
            return None

    @classmethod
    def _capture_via_qscreen(cls, file_path: Path) -> Optional[Path]:
        """Fallback method using PySide6 QGuiApplication."""
        try:
            from PySide6.QtGui import QGuiApplication
            app = QGuiApplication.instance()
            if not app:
                logger.error("No QGuiApplication instance available for QScreen capture.")
                return None
            screen = QGuiApplication.primaryScreen()
            if not screen:
                logger.error("No primary QScreen available.")
                return None
            pixmap = screen.grabWindow(0)
            pixmap.save(str(file_path), "PNG")
            logger.info(f"Captured screen via QScreen fallback: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"QScreen capture fallback failed: {e}")
            return None
