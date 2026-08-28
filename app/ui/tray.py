"""Windows System Tray integration module."""

from PySide6.QtCore import QObject
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from app.core.config import get_assets_dir
from app.core.events import get_event_bus
from app.startup.windows_startup import WindowsStartupManager

class SystemTrayManager(QObject):
    """Manages system tray icon and context menu."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.event_bus = get_event_bus()

        self.tray_icon = QSystemTrayIcon(self)

        icon_path = get_assets_dir() / "icon.png"
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))

        self.tray_icon.setToolTip("AIPet - AI Desktop Companion")

        self._setup_menu()
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _setup_menu(self):
        menu = QMenu()

        chat_act = QAction("Open Chat", self)
        chat_act.triggered.connect(lambda: self.event_bus.chat_requested.emit())
        menu.addAction(chat_act)

        screen_act = QAction("Analyze Screen", self)
        screen_act.triggered.connect(lambda: self.event_bus.screen_analysis_requested.emit())
        menu.addAction(screen_act)

        menu.addSeparator()

        settings_act = QAction("Settings", self)
        settings_act.triggered.connect(self._open_settings)
        menu.addAction(settings_act)

        startup_act = QAction("Start with Windows", self, checkable=True)
        startup_act.setChecked(WindowsStartupManager.is_startup_enabled())
        startup_act.triggered.connect(self._toggle_startup)
        menu.addAction(startup_act)
        self.startup_act = startup_act

        menu.addSeparator()

        about_act = QAction("About AIPet", self)
        about_act.triggered.connect(self._show_about)
        menu.addAction(about_act)

        exit_act = QAction("Exit", self)
        exit_act.triggered.connect(lambda: self.event_bus.exit_requested.emit())
        menu.addAction(exit_act)

        self.tray_icon.setContextMenu(menu)

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger or reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.event_bus.chat_requested.emit()

    def _open_settings(self):
        if hasattr(self, "settings_win") and self.settings_win:
            self.settings_win.show()
            self.settings_win.raise_()
        else:
            from app.ui.settings_window import SettingsWindow
            self.settings_win = SettingsWindow()
            self.settings_win.show()

    def _toggle_startup(self, checked: bool):
        WindowsStartupManager.set_startup(checked)

    def _show_about(self):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            None,
            "About AIPet",
            "<b>AIPet v1.0</b><br>"
            "An interactive AI desktop pet featuring multi-modal screen analysis, "
            "NVIDIA NIM vision model integration, and safe desktop automation.<br><br>"
            "Created for Windows."
        )
