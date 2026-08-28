"""Mouse control implementation for Windows with PySide6 fallback."""

import sys
import time
import ctypes
from typing import Tuple, Optional
from app.core.logger import logger

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    user32 = ctypes.windll.user32

class MouseController:
    """Handles mouse movement, clicking, double clicking, right clicking, and scrolling."""

    MOUSEEVENTF_MOVE = 0x0001
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_RIGHTDOWN = 0x0008
    MOUSEEVENTF_RIGHTUP = 0x0010
    MOUSEEVENTF_MIDDLEDOWN = 0x0020
    MOUSEEVENTF_MIDDLEUP = 0x0040
    MOUSEEVENTF_WHEEL = 0x0800
    MOUSEEVENTF_ABSOLUTE = 0x8000

    @classmethod
    def get_position(cls) -> Tuple[int, int]:
        if IS_WINDOWS:
            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            pt = POINT()
            user32.GetCursorPos(ctypes.byref(pt))
            return (pt.x, pt.y)
        else:
            try:
                from PySide6.QtGui import QCursor
                pos = QCursor.pos()
                return (pos.x(), pos.y())
            except Exception:
                return (0, 0)

    @classmethod
    def move(cls, x: int, y: int) -> bool:
        try:
            if IS_WINDOWS:
                user32.SetCursorPos(int(x), int(y))
            else:
                from PySide6.QtGui import QCursor
                QCursor.setPos(int(x), int(y))
            logger.info(f"Moved mouse to ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Failed to move mouse to ({x}, {y}): {e}")
            return False

    @classmethod
    def click(cls, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        try:
            if x is not None and y is not None:
                cls.move(x, y)
                time.sleep(0.05)

            if IS_WINDOWS:
                user32.mouse_event(cls.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                time.sleep(0.05)
                user32.mouse_event(cls.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            logger.info(f"Executed mouse left click at {cls.get_position()}")
            return True
        except Exception as e:
            logger.error(f"Mouse click failed: {e}")
            return False

    @classmethod
    def double_click(cls, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        try:
            cls.click(x, y)
            time.sleep(0.1)
            cls.click()
            logger.info("Executed mouse double click")
            return True
        except Exception as e:
            logger.error(f"Mouse double click failed: {e}")
            return False

    @classmethod
    def right_click(cls, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        try:
            if x is not None and y is not None:
                cls.move(x, y)
                time.sleep(0.05)

            if IS_WINDOWS:
                user32.mouse_event(cls.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
                time.sleep(0.05)
                user32.mouse_event(cls.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
            logger.info(f"Executed mouse right click at {cls.get_position()}")
            return True
        except Exception as e:
            logger.error(f"Mouse right click failed: {e}")
            return False

    @classmethod
    def scroll(cls, clicks: int) -> bool:
        try:
            if IS_WINDOWS:
                # 120 units per notch in Windows mouse_event
                dw_data = clicks * 120
                user32.mouse_event(cls.MOUSEEVENTF_WHEEL, 0, 0, dw_data, 0)
            logger.info(f"Scrolled mouse wheel by {clicks} units")
            return True
        except Exception as e:
            logger.error(f"Mouse scroll failed: {e}")
            return False
