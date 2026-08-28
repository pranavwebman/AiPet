"""Active window detection module for Windows with cross-platform fallback."""

import sys
import ctypes
from typing import Dict, Any, Optional
from app.core.logger import logger

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    psapi = ctypes.windll.psapi

class ActiveWindowDetector:
    """Retrieves information about the currently active foreground window."""

    @classmethod
    def get_active_window_info(cls) -> Dict[str, Any]:
        """
        Returns dictionary containing:
        - title: str
        - process_name: str
        - app_name: str
        - bounds: (left, top, width, height)
        """
        if not IS_WINDOWS:
            return {
                "title": "Desktop Environment",
                "process_name": "desktop.exe",
                "app_name": "Desktop",
                "bounds": (0, 0, 1920, 1080),
                "hwnd": 0
            }

        try:
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return cls._empty_info()

            # Get Window Title
            length = user32.GetWindowTextLengthW(hwnd)
            title_buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, title_buf, length + 1)
            title = title_buf.value

            # Get Process Name
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            process_name = cls._get_process_name(pid.value)

            # Get Window Bounds
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            left = rect.left
            top = rect.top
            width = rect.right - rect.left
            height = rect.bottom - rect.top

            # Clean Application Name
            app_name = process_name.replace(".exe", "").capitalize() if process_name else "Unknown"

            info = {
                "title": title or "Untitled Window",
                "process_name": process_name or "unknown.exe",
                "app_name": app_name,
                "bounds": (left, top, width, height),
                "hwnd": hwnd
            }
            logger.debug(f"Active window detected: {info}")
            return info

        except Exception as e:
            logger.error(f"Error getting active window info: {e}")
            return cls._empty_info()

    @classmethod
    def _get_process_name(cls, pid: int) -> str:
        PROCESS_QUERY_INFORMATION = 0x0400
        PROCESS_VM_READ = 0x0010
        h_process = ctypes.windll.kernel32.OpenProcess(
            PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid
        )
        if not h_process:
            return "unknown.exe"

        try:
            buf = ctypes.create_unicode_buffer(1024)
            if psapi.GetModuleFileNameExW(h_process, 0, buf, 1024):
                path = buf.value
                return path.split("\\")[-1]
            return "unknown.exe"
        finally:
            ctypes.windll.kernel32.CloseHandle(h_process)

    @classmethod
    def _empty_info(cls) -> Dict[str, Any]:
        return {
            "title": "Desktop",
            "process_name": "explorer.exe",
            "app_name": "Explorer",
            "bounds": (0, 0, 1920, 1080),
            "hwnd": 0
        }
