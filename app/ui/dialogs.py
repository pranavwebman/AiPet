"""Action Confirmation Dialog for consequential computer control actions."""

from typing import Dict, Any, Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QFrame
)
from app.core.config import get_assets_dir
from PySide6.QtGui import QIcon

class ActionConfirmationDialog(QDialog):
    """Dialog prompting user confirmation before executing consequential desktop actions."""

    def __init__(self, action: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.action = action
        self.confirmed = False

        self.setWindowTitle("AIPet - Security Confirmation")
        self.setFixedSize(400, 260)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        icon_path = get_assets_dir() / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Header Title
        title_label = QLabel("<b>AIPet wants to perform a computer action:</b>", self)
        title_label.setStyleSheet("font-size: 14px; color: #1E293B;")
        layout.addWidget(title_label)

        # Action Details Box
        desc_box = QFrame(self)
        desc_box.setFrameShape(QFrame.StyledPanel)
        desc_box.setStyleSheet("background-color: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px;")
        box_layout = QVBoxLayout(desc_box)

        action_type = self.action.get("type", "unknown").upper()
        description = self.action.get("description", "No description provided.")

        type_lbl = QLabel(f"<b>Action Type:</b> {action_type}")
        type_lbl.setStyleSheet("color: #0F172A;")
        desc_lbl = QLabel(f"<b>Description:</b> {description}")
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color: #334155;")

        box_layout.addWidget(type_lbl)
        box_layout.addWidget(desc_lbl)

        # Detail Payload preview
        details_text = "\n".join(f"{k}: {v}" for k, v in self.action.items() if k not in ("type", "description"))
        if details_text:
            param_lbl = QLabel(f"<b>Parameters:</b> {details_text}")
            param_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
            box_layout.addWidget(param_lbl)

        layout.addWidget(desc_box)

        # Warning text
        warn_lbl = QLabel("Do you allow AIPet to execute this action?", self)
        warn_lbl.setStyleSheet("font-size: 12px; color: #475569;")
        layout.addWidget(warn_lbl)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Deny / Cancel", self)
        btn_cancel.setStyleSheet("padding: 6px 16px; background-color: #E2E8F0; color: #334155; border-radius: 4px;")
        btn_cancel.clicked.connect(self.reject)

        btn_allow = QPushButton("Allow Action", self)
        btn_allow.setStyleSheet("padding: 6px 16px; background-color: #2563EB; color: white; font-weight: bold; border-radius: 4px;")
        btn_allow.clicked.connect(self._on_allow)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_allow)

        layout.addLayout(btn_layout)

    def _on_allow(self):
        self.confirmed = True
        self.accept()
