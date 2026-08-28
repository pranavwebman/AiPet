"""Settings window for persistent AIPet configuration."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QLineEdit, QCheckBox, QDoubleSpinBox, QSpinBox,
    QPushButton, QComboBox, QMessageBox, QFormLayout, QGroupBox
)
from app.core.config import get_config, get_assets_dir
from app.core.events import get_event_bus
from app.startup.windows_startup import WindowsStartupManager
from app.memory.conversation_store import ConversationStore

class SettingsWindow(QMainWindow):
    """Tabbed configuration window for AIPet settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = get_config()
        self.event_bus = get_event_bus()

        self.setWindowTitle("AIPet - Settings")
        self.resize(500, 480)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)

        icon_path = get_assets_dir() / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.tabs = QTabWidget(self)

        # 1. General Tab
        self.tab_general = QWidget()
        self._setup_general_tab()
        self.tabs.addTab(self.tab_general, "General")

        # 2. AI Tab
        self.tab_ai = QWidget()
        self._setup_ai_tab()
        self.tabs.addTab(self.tab_ai, "AI Model")

        # 3. Screen Tab
        self.tab_screen = QWidget()
        self._setup_screen_tab()
        self.tabs.addTab(self.tab_screen, "Screen")

        # 4. Automation Tab
        self.tab_automation = QWidget()
        self._setup_automation_tab()
        self.tabs.addTab(self.tab_automation, "Automation")

        # 5. Memory Tab
        self.tab_memory = QWidget()
        self._setup_memory_tab()
        self.tabs.addTab(self.tab_memory, "Memory")

        layout.addWidget(self.tabs)

        # Bottom Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancel", self)
        btn_cancel.clicked.connect(self.close)

        btn_save = QPushButton("Save & Apply", self)
        btn_save.setStyleSheet("padding: 6px 16px; background-color: #2563EB; color: white; font-weight: bold; border-radius: 4px;")
        btn_save.clicked.connect(self._save_settings)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)

    def _setup_general_tab(self):
        layout = QFormLayout(self.tab_general)
        layout.setContentsMargins(15, 15, 15, 15)

        self.chk_startup = QCheckBox("Start automatically with Windows", self)
        self.chk_always_top = QCheckBox("Pet stays always on top", self)
        self.chk_animations = QCheckBox("Enable idle pet animations", self)
        self.txt_hotkey = QLineEdit("Ctrl+Alt+Space", self)

        layout.addRow("Startup:", self.chk_startup)
        layout.addRow("Display:", self.chk_always_top)
        layout.addRow("Animations:", self.chk_animations)
        layout.addRow("Global Hotkey:", self.txt_hotkey)

    def _setup_ai_tab(self):
        layout = QFormLayout(self.tab_ai)
        layout.setContentsMargins(15, 15, 15, 15)

        self.cmb_provider = QComboBox(self)
        self.cmb_provider.addItems(["NVIDIA NIM"])

        self.txt_api_key = QLineEdit(self)
        self.txt_api_key.setEchoMode(QLineEdit.Password)
        self.txt_api_key.setPlaceholderText("nvapi-...")

        self.txt_model = QLineEdit(self)
        self.txt_endpoint = QLineEdit(self)

        self.spin_temp = QDoubleSpinBox(self)
        self.spin_temp.setRange(0.0, 1.5)
        self.spin_temp.setSingleStep(0.1)

        self.spin_tokens = QSpinBox(self)
        self.spin_tokens.setRange(100, 8192)

        layout.addRow("Provider:", self.cmb_provider)
        layout.addRow("NVIDIA API Key:", self.txt_api_key)
        layout.addRow("Model Name:", self.txt_model)
        layout.addRow("API Endpoint:", self.txt_endpoint)
        layout.addRow("Temperature:", self.spin_temp)
        layout.addRow("Max Tokens:", self.spin_tokens)

    def _setup_screen_tab(self):
        layout = QFormLayout(self.tab_screen)
        layout.setContentsMargins(15, 15, 15, 15)

        self.chk_screen_analysis = QCheckBox("Enable explicit screen capture and analysis", self)
        self.chk_active_only = QCheckBox("Analyze active window only (if unchecked, captures full screen)", self)
        self.chk_ocr = QCheckBox("Enable OCR text extraction from screenshots", self)

        layout.addRow("Screen Awareness:", self.chk_screen_analysis)
        layout.addRow("Capture Mode:", self.chk_active_only)
        layout.addRow("OCR Support:", self.chk_ocr)

    def _setup_automation_tab(self):
        layout = QFormLayout(self.tab_automation)
        layout.setContentsMargins(15, 15, 15, 15)

        self.chk_computer_control = QCheckBox("Enable computer mouse & keyboard control", self)
        self.chk_require_confirm = QCheckBox("Require user confirmation before executing actions", self)
        self.cmb_confirm_level = QComboBox(self)
        self.cmb_confirm_level.addItems(["consequential", "all"])

        layout.addRow("Computer Control:", self.chk_computer_control)
        layout.addRow("Safety Prompt:", self.chk_require_confirm)
        layout.addRow("Confirmation Level:", self.cmb_confirm_level)

    def _setup_memory_tab(self):
        layout = QFormLayout(self.tab_memory)
        layout.setContentsMargins(15, 15, 15, 15)

        self.chk_memory = QCheckBox("Enable persistent conversation memory (SQLite)", self)

        btn_clear_data = QPushButton("Clear All Stored Conversations", self)
        btn_clear_data.setStyleSheet("background-color: #EF476F; color: white; padding: 6px;")
        btn_clear_data.clicked.connect(self._clear_memory)

        layout.addRow("Memory Persistence:", self.chk_memory)
        layout.addRow("Clear History:", btn_clear_data)

    def _load_settings(self):
        c = self.config
        self.chk_startup.setChecked(bool(c.get("start_with_windows", False)))
        self.chk_always_top.setChecked(bool(c.get("always_on_top", True)))
        self.chk_animations.setChecked(bool(c.get("enable_animations", True)))
        self.txt_hotkey.setText(c.get("global_hotkey", "Ctrl+Alt+Space"))

        self.txt_api_key.setText(c.get("nvidia_api_key", ""))
        self.txt_model.setText(c.get("model_name", "meta/llama-3.2-11b-vision-instruct"))
        self.txt_endpoint.setText(c.get("api_endpoint", "https://integrate.api.nvidia.com/v1"))
        self.spin_temp.setValue(float(c.get("temperature", 0.7)))
        self.spin_tokens.setValue(int(c.get("max_tokens", 1024)))

        self.chk_screen_analysis.setChecked(bool(c.get("enable_screen_analysis", True)))
        self.chk_active_only.setChecked(bool(c.get("analyze_active_window_only", False)))
        self.chk_ocr.setChecked(bool(c.get("enable_ocr", True)))

        self.chk_computer_control.setChecked(bool(c.get("enable_computer_control", True)))
        self.chk_require_confirm.setChecked(bool(c.get("require_confirmation", True)))

        idx = self.cmb_confirm_level.findText(c.get("confirmation_level", "consequential"))
        if idx >= 0:
            self.cmb_confirm_level.setCurrentIndex(idx)

        self.chk_memory.setChecked(bool(c.get("enable_memory", True)))

    def _save_settings(self):
        startup_val = self.chk_startup.isChecked()

        # Apply Windows startup setting
        WindowsStartupManager.set_startup(startup_val)

        c = self.config
        c.set("start_with_windows", startup_val)
        c.set("always_on_top", self.chk_always_top.isChecked())
        c.set("enable_animations", self.chk_animations.isChecked())
        c.set("global_hotkey", self.txt_hotkey.text().strip())

        c.set("nvidia_api_key", self.txt_api_key.text().strip())
        c.set("model_name", self.txt_model.text().strip())
        c.set("api_endpoint", self.txt_endpoint.text().strip())
        c.set("temperature", self.spin_temp.value())
        c.set("max_tokens", self.spin_tokens.value())

        c.set("enable_screen_analysis", self.chk_screen_analysis.isChecked())
        c.set("analyze_active_window_only", self.chk_active_only.isChecked())
        c.set("enable_ocr", self.chk_ocr.isChecked())

        c.set("enable_computer_control", self.chk_computer_control.isChecked())
        c.set("require_confirmation", self.chk_require_confirm.isChecked())
        c.set("confirmation_level", self.cmb_confirm_level.currentText())

        c.set("enable_memory", self.chk_memory.isChecked())

        self.event_bus.settings_changed.emit()
        QMessageBox.information(self, "Settings Saved", "AIPet configuration saved successfully.")
        self.close()

    def _clear_memory(self):
        reply = QMessageBox.question(
            self, "Clear History", "Are you sure you want to clear all stored conversation history?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            store = ConversationStore()
            store.clear_history()
            QMessageBox.information(self, "Cleared", "Conversation history cleared.")
