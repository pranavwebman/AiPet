"""Global Hotkey listener for Windows using RegisterHotKey and PySide6 QThread."""

import sys
import ctypes
from PySide6.QtCore import QThread, Signal
from app.core.logger import logger

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    from ctypes import wintypes
    user32 = ctypes.windll.user32

    # Constants
    MOD_ALT = 0x0001
    MOD_CONTROL = 0x0002
    MOD_SHIFT = 0x0004
    MOD_WIN = 0x0008
    WM_HOTKEY = 0x0312

    VK_SPACE = 0x20

class GlobalHotkeyThread(QThread):
    """Worker thread listening for OS-wide global hotkey triggers."""

    hotkey_triggered = Signal()

    def __init__(self, key_combination: str = "Ctrl+Alt+Space", parent=None):
        super().__init__(parent)
        self.key_combination = key_combination
        self.hotkey_id = 101
        self._running = True

    def run(self):
        if not IS_WINDOWS:
            logger.info("Global hotkey Windows listener skipped on non-Windows platform.")
            return

        # Parse modifiers and key
        parts = [p.strip().lower() for p in self.key_combination.split("+")]
        fs_modifiers = 0
        vk_code = VK_SPACE

        for p in parts:
            if p in ("ctrl", "control"):
                fs_modifiers |= MOD_CONTROL
            elif p == "alt":
                fs_modifiers |= MOD_ALT
            elif p == "shift":
                fs_modifiers |= MOD_SHIFT
            elif p in ("win", "cmd"):
                fs_modifiers |= MOD_WIN
            elif p == "space":
                vk_code = VK_SPACE

        res = user32.RegisterHotKey(None, self.hotkey_id, fs_modifiers, vk_code)
        if not res:
            logger.error(f"Failed to register Windows global hotkey {self.key_combination}")
            return

        logger.info(f"Registered Windows global hotkey: {self.key_combination}")

        msg = wintypes.MSG()
        try:
            while self._running:
                # Peek or Get message loop
                if user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                    if msg.message == WM_HOTKEY and msg.wParam == self.hotkey_id:
                        logger.info("Windows global hotkey triggered!")
                        self.hotkey_triggered.emit()
                    user32.TranslateMessage(ctypes.byref(msg))
                    user32.DispatchMessageW(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, self.hotkey_id)

    def stop(self):
        self._running = False
        if IS_WINDOWS:
            user32.PostThreadMessageW(int(self.currentThreadId()), 0x0000, 0, 0) # WM_QUIT
        self.wait(1000)
