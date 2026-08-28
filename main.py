"""Main application entrypoint for AIPet."""

import sys
import os
import traceback
from pathlib import Path

# Ensure app root is on python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtCore import Qt, QObject, QEvent
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon, QShortcut, QKeySequence

from app.core.config import get_config, get_assets_dir
from app.core.logger import logger
from app.core.events import get_event_bus
from app.pet.pet_window import PetWindow
from app.ui.chat_window import ChatWindow
from app.ui.settings_window import SettingsWindow
from app.ui.tray import SystemTrayManager
from app.ui.global_hotkey import GlobalHotkeyThread

def global_exception_handler(exctype, value, tb):
    """Global exception handler logging unhandled crashes."""
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    logger.critical(f"Unhandled Exception: {err_msg}")
    print(f"Unhandled Exception: {err_msg}", file=sys.stderr)

class AIPetApplication:
    """Master application wrapper managing lifecycle and main event loop."""

    def __init__(self):
        sys.excepthook = global_exception_handler

        self.app = QApplication.instance() or QApplication(sys.argv)
        self.app.setApplicationName("AIPet")
        self.app.setQuitOnLastWindowClosed(False) # Remain running in tray

        icon_path = get_assets_dir() / "icon.png"
        if icon_path.exists():
            self.app.setWindowIcon(QIcon(str(icon_path)))

        self.config = get_config()
        self.event_bus = get_event_bus()

        # Instantiate components
        self.pet_window = PetWindow()
        self.chat_window = ChatWindow()
        self.settings_window = SettingsWindow()
        self.tray_manager = SystemTrayManager()

        self._wire_signals()
        self._setup_global_hotkey()

    def _wire_signals(self):
        self.event_bus.chat_requested.connect(self._on_chat_requested)
        self.event_bus.exit_requested.connect(self.shutdown)

    def _setup_global_hotkey(self):
        hotkey_str = self.config.get("global_hotkey", "Ctrl+Alt+Space")

        # 1. Native OS Global Hotkey Listener Thread
        self.hotkey_thread = GlobalHotkeyThread(key_combination=hotkey_str, parent=self.pet_window)
        self.hotkey_thread.hotkey_triggered.connect(self._on_chat_requested)
        self.hotkey_thread.start()

        # 2. Local Fallback Qt Shortcut
        try:
            self.shortcut = QShortcut(QKeySequence(hotkey_str), self.pet_window)
            self.shortcut.activated.connect(self._on_chat_requested)
            logger.info(f"Registered hotkey shortcut: {hotkey_str}")
        except Exception as e:
            logger.error(f"Failed to register local hotkey: {e}")

    def _on_chat_requested(self):
        self.chat_window.show_and_focus()

    def run(self) -> int:
        # Check API key configuration on launch
        api_key = self.config.get("nvidia_api_key", "").strip()
        if not api_key:
            logger.info("No NVIDIA API key configured on startup.")
            QMessageBox.information(
                None,
                "NVIDIA API Key Required",
                "Welcome to AIPet!\n\nPlease configure your NVIDIA NIM API key in Settings to enable AI chat and screen analysis features."
            )
            self.settings_window.show()

        self.pet_window.show()
        logger.info("AIPet application launched successfully.")
        return self.app.exec()

    def shutdown(self):
        logger.info("Shutting down AIPet application...")
        if hasattr(self, "hotkey_thread") and self.hotkey_thread.isRunning():
            self.hotkey_thread.stop()
        self.app.quit()

def main():
    app_inst = AIPetApplication()
    sys.exit(app_inst.run())

if __name__ == "__main__":
    main()
