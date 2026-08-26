"""Windows API automation routines (window focusing, closing, enumerating)."""

import sys
import ctypes
from typing import List, Dict, Any, Optional
from app.core.logger import logger

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    user32 = ctypes.windll.user32

class WindowsAutomation:
    """Provides methods for focusing windows, closing windows, and enumerating UI components."""

    @classmethod
    def focus_window_by_title(cls, title_substring: str) -> bool:
        """Find window by title and bring it to foreground."""
        if not title_substring:
            return False

        if not IS_WINDOWS:
            logger.info(f"Mock focusing window containing '{title_substring}'")
            return True

        target_hwnd = [None]

        def enum_windows_callback(hwnd, extra):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    title = buf.value
                    if title_substring.lower() in title.lower():
                        target_hwnd[0] = hwnd
                        return False # Stop enumeration
            return True # Continue

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)

        hwnd = target_hwnd[0]
        if hwnd:
            try:
                # Restore window if minimized
                SW_RESTORE = 9
                user32.ShowWindow(hwnd, SW_RESTORE)
                user32.SetForegroundWindow(hwnd)
                logger.info(f"Focused window matching '{title_substring}' (HWND {hwnd})")
                return True
            except Exception as e:
                logger.error(f"Failed to bring window to foreground: {e}")
                return False

        logger.warning(f"No visible window found matching title '{title_substring}'")
        return False

    @classmethod
    def close_window_by_title(cls, title_substring: str) -> bool:
        """Send WM_CLOSE signal to target window."""
        if not title_substring or not IS_WINDOWS:
            return False

        target_hwnd = [None]

        def enum_windows_callback(hwnd, extra):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    title = buf.value
                    if title_substring.lower() in title.lower():
                        target_hwnd[0] = hwnd
                        return False
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)

        hwnd = target_hwnd[0]
        if hwnd:
            try:
                WM_CLOSE = 0x0010
                user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
                logger.info(f"Sent WM_CLOSE to window matching '{title_substring}'")
                return True
            except Exception as e:
                logger.error(f"Failed to close window: {e}")
                return False

        return False
