"""Interactive Chat Window interface for AIPet."""

from pathlib import Path
from typing import Optional, Dict, Any, List
from PySide6.QtCore import Qt, QEvent, QTimer
from PySide6.QtGui import QIcon, QTextCursor, QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPlainTextEdit,
    QPushButton, QLabel, QFileDialog, QFrame, QMessageBox, QSplitter
)
from app.core.config import get_assets_dir, get_config
from app.core.events import get_event_bus
from app.ai.conversation import ConversationManager
from app.vision.screen_capture import ScreenCapturer
from app.automation.action_executor import ActionExecutor
from app.ui.dialogs import ActionConfirmationDialog
from app.core.logger import logger

class MultilineInputEdit(QPlainTextEdit):
    """Custom text area sending message on Enter and new line on Shift+Enter."""

    def __init__(self, send_callback, parent=None):
        super().__init__(parent)
        self.send_callback = send_callback
        self.setPlaceholderText("Type a message to AIPet... (Enter to send, Shift+Enter for new line)")
        self.setMaximumHeight(80)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if event.modifiers() & Qt.ShiftModifier:
                super().keyPressEvent(event)
            else:
                self.send_callback()
                event.accept()
        else:
            super().keyPressEvent(event)

class ChatWindow(QMainWindow):
    """Modern chat window supporting message history, vision requests, and action execution."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.event_bus = get_event_bus()
        self.conv_manager = ConversationManager()
        self.attached_image_path: Optional[Path] = None

        self.setWindowTitle("AIPet - Interactive Chat")
        self.resize(420, 560)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)

        icon_path = get_assets_dir() / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self._setup_ui()

        # Connect signals
        self.event_bus.screen_analysis_requested.connect(self.trigger_screen_analysis)
        self.event_bus.ai_response_received.connect(self._on_ai_response)
        self.event_bus.ai_error_occurred.connect(self._on_ai_error)

        # Load recent chat history
        self._load_history()

    def _setup_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Top Header Bar
        header_layout = QHBoxLayout()
        header_title = QLabel("🤖 <b>AIPet Assistant</b>", self)
        header_title.setStyleSheet("font-size: 15px; color: #1E293B;")

        btn_clear = QPushButton("Clear Chat", self)
        btn_clear.setStyleSheet("font-size: 11px; padding: 4px 8px;")
        btn_clear.clicked.connect(self._clear_chat)

        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addWidget(btn_clear)
        layout.addLayout(header_layout)

        # Chat History Display
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet(
            "background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 8px;"
        )
        layout.addWidget(self.chat_display, stretch=1)

        # Status / Typing indicator label
        self.status_lbl = QLabel("", self)
        self.status_lbl.setStyleSheet("color: #64748B; font-style: italic; font-size: 12px;")
        layout.addWidget(self.status_lbl)

        # Image Attachment Status Indicator
        self.attach_lbl = QLabel("", self)
        self.attach_lbl.setStyleSheet("color: #2563EB; font-weight: bold; font-size: 11px;")
        self.attach_lbl.setVisible(False)
        layout.addWidget(self.attach_lbl)

        # Input controls section
        input_layout = QHBoxLayout()

        self.input_edit = MultilineInputEdit(self.send_message, self)
        input_layout.addWidget(self.input_edit, stretch=1)

        btn_screen = QPushButton("📷 Look Screen", self)
        btn_screen.setToolTip("Capture screen and analyze with AIPet")
        btn_screen.setStyleSheet("padding: 8px 10px; background-color: #0EA5E9; color: white; border-radius: 4px;")
        btn_screen.clicked.connect(self.trigger_screen_analysis)

        btn_send = QPushButton("Send", self)
        btn_send.setStyleSheet("padding: 8px 16px; background-color: #2563EB; color: white; font-weight: bold; border-radius: 4px;")
        btn_send.clicked.connect(self.send_message)

        btn_box = QVBoxLayout()
        btn_box.addWidget(btn_screen)
        btn_box.addWidget(btn_send)
        input_layout.addLayout(btn_box)

        layout.addLayout(input_layout)

    def _load_history(self):
        self.chat_display.clear()
        recent = self.conv_manager.store.get_recent_messages(limit=30)
        for msg in recent:
            role = msg["role"]
            content = msg["content"]
            self._append_message_ui(role, content)

    def _append_message_ui(self, role: str, content: str):
        if role == "user":
            formatted = f'<div style="margin: 6px 0; text-align: right;"><span style="background-color: #DBEAFE; color: #1E3A8A; padding: 6px 10px; border-radius: 8px; display: inline-block;"><b>You:</b> {content}</span></div>'
        elif role == "assistant":
            formatted = f'<div style="margin: 6px 0; text-align: left;"><span style="background-color: #F1F5F9; color: #0F172A; padding: 6px 10px; border-radius: 8px; display: inline-block;"><b>AIPet:</b> {content}</span></div>'
        else:
            formatted = f'<div style="margin: 4px 0; text-align: center; color: #EF476F;"><i>{content}</i></div>'

        self.chat_display.append(formatted)
        self.chat_display.moveCursor(QTextCursor.End)

    def send_message(self):
        text = self.input_edit.toPlainText().strip()
        if not text and not self.attached_image_path:
            return

        img_path = self.attached_image_path
        self.attached_image_path = None
        self.attach_lbl.setVisible(False)
        self.input_edit.clear()

        # Append to UI immediately
        display_text = text if text else "[Requested Screen Analysis]"
        self._append_message_ui("user", display_text)

        # Update pet state and status
        self.event_bus.pet_state_changed.emit("thinking")
        self.status_lbl.setText("AIPet is thinking...")

        # Send to AI worker thread
        self.conv_manager.process_user_message(
            text_prompt=display_text,
            image_path=img_path,
            on_response=self._handle_ai_response_with_actions,
            on_error=self._on_ai_error
        )

    def trigger_screen_analysis(self):
        config = get_config()
        if not config.get("enable_screen_analysis", True):
            QMessageBox.warning(self, "Screen Analysis Disabled", "Screen analysis is disabled in settings.")
            return

        self.status_lbl.setText("Capturing desktop screen...")
        shot_path = ScreenCapturer.capture_full_screen()
        if shot_path and shot_path.exists():
            self.attached_image_path = shot_path
            self.attach_lbl.setText("📷 Screen capture attached to next message!")
            self.attach_lbl.setVisible(True)
            self.status_lbl.setText("Screen captured.")
            if not self.input_edit.toPlainText().strip():
                self.input_edit.setPlainText("Please analyze my screen and explain what you see.")
        else:
            QMessageBox.critical(self, "Capture Error", "Failed to capture desktop screenshot.")
            self.status_lbl.setText("Screen capture failed.")

    def _handle_ai_response_with_actions(self, response_text: str, actions: list):
        self.event_bus.pet_state_changed.emit("talking")
        self.status_lbl.setText("")

        # Handle parsed computer automation actions
        if actions:
            logger.info(f"AI requested computer actions: {actions}")
            for action in actions:
                res, msg = ActionExecutor.execute_action(action, user_confirmed=False)
                if msg == "REQUIRES_CONFIRMATION":
                    dlg = ActionConfirmationDialog(action, self)
                    if dlg.exec() == ActionConfirmationDialog.Accepted:
                        exec_res, exec_msg = ActionExecutor.execute_action(action, user_confirmed=True)
                        self._append_message_ui("system", f"Action Executed: {exec_msg}")
                    else:
                        self._append_message_ui("system", f"Action Cancelled by User: {action.get('type')}")
                elif res:
                    self._append_message_ui("system", f"Executed: {msg}")
                else:
                    self._append_message_ui("system", f"Action Failed: {msg}")

    def _on_ai_response(self, response_text: str):
        self._append_message_ui("assistant", response_text)

    def _on_ai_error(self, err_msg: str):
        self.event_bus.pet_state_changed.emit("error")
        self.status_lbl.setText("")
        self._append_message_ui("system", f"Error: {err_msg}")

    def _clear_chat(self):
        self.conv_manager.store.clear_history()
        self.chat_display.clear()
        self.status_lbl.setText("Conversation history cleared.")

    def show_and_focus(self):
        self.show()
        self.raise_()
        self.activateWindow()
        self.input_edit.setFocus()
