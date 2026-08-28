"""Transparent, frameless, draggable PySide6 desktop pet window."""

from PySide6.QtCore import Qt, QPoint, QSize
from PySide6.QtGui import QPixmap, QMouseEvent, QContextMenuEvent, QAction, QGuiApplication
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QMenu
from app.pet.animation import PetAnimationEngine
from app.pet.behavior import PetBehaviorController
from app.pet.movement import PetMovementController
from app.core.events import get_event_bus
from app.core.config import get_config
from app.core.logger import logger

class PetWindow(QWidget):
    """Transparent always-on-top window representing the AI Desktop Pet."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.event_bus = get_event_bus()

        self._drag_active = False
        self._drag_start_pos = QPoint()
        self._mouse_press_global_pos = QPoint()

        # Window Flags: Transparent, Frameless, Always-On-Top, Tool window (no taskbar item)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

        # Setup UI layout and image label
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        layout.addWidget(self.label)

        # Animation Engine & Behavior
        self.anim = PetAnimationEngine(self)
        self.anim.state_changed.connect(self._on_animation_state_changed)
        self.behavior = PetBehaviorController(self.anim, self)

        # Position memory
        init_x, init_y = PetMovementController.get_saved_position()
        self.move(init_x, init_y)
        self.setFixedSize(QSize(128, 128))

        # Initial display
        self._on_animation_state_changed("idle", self.anim.get_current_pixmap())

        # Connect event bus signals
        self.event_bus.pet_state_changed.connect(self._set_state_from_event)

    def _set_state_from_event(self, state: str) -> None:
        self.anim.set_state(state, duration_ms=4000)

    def _on_animation_state_changed(self, state: str, pixmap: QPixmap) -> None:
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                128, 128,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.label.setPixmap(scaled)

    def enterEvent(self, event) -> None:
        if self.anim.current_state == "idle":
            self.anim.set_state("hover")
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        if self.anim.current_state == "hover":
            self.anim.set_state("idle")
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = True
            self._mouse_press_global_pos = event.globalPosition().toPoint()
            self._drag_start_pos = self._mouse_press_global_pos - self.frameGeometry().topLeft()
            self.anim.set_state("clicked", duration_ms=1000)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_active and event.buttons() & Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self._drag_start_pos
            self._constrain_and_move(new_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._drag_active:
            self._drag_active = False
            PetMovementController.save_position(self.x(), self.y())

            # Check if this was a simple click (small movement threshold) rather than a drag
            release_pos = event.globalPosition().toPoint()
            distance = (release_pos - self._mouse_press_global_pos).manhattanLength()
            if distance < 6:
                self.event_bus.chat_requested.emit()

            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.anim.set_state("happy", duration_ms=2000)
            self.event_bus.chat_requested.emit()
            event.accept()

    def _constrain_and_move(self, target_pos: QPoint) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geom = screen.availableGeometry()
            x = max(screen_geom.left(), min(target_pos.x(), screen_geom.right() - self.width()))
            y = max(screen_geom.top(), min(target_pos.y(), screen_geom.bottom() - self.height()))
            self.move(x, y)
        else:
            self.move(target_pos)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = QMenu(self)

        chat_action = menu.addAction("Chat")
        chat_action.triggered.connect(lambda: self.event_bus.chat_requested.emit())

        analyze_action = menu.addAction("Analyze Screen")
        analyze_action.triggered.connect(lambda: self.event_bus.screen_analysis_requested.emit())

        menu.addSeparator()

        settings_action = menu.addAction("Settings")
        settings_action.triggered.connect(self._open_settings)

        if self.behavior.is_paused:
            pause_action = menu.addAction("Resume Pet")
            pause_action.triggered.connect(lambda: self.behavior.set_paused(False))
        else:
            pause_action = menu.addAction("Pause Pet")
            pause_action.triggered.connect(lambda: self.behavior.set_paused(True))

        about_action = menu.addAction("About")
        about_action.triggered.connect(self._show_about)

        menu.addSeparator()

        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(lambda: self.event_bus.exit_requested.emit())

        menu.exec_(event.globalPos())

    def _open_settings(self):
        from app.ui.settings_window import SettingsWindow
        if not hasattr(self, "_settings_win") or self._settings_win is None:
            self._settings_win = SettingsWindow()
        self._settings_win.show()
        self._settings_win.raise_()

    def _show_about(self):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "About AIPet",
            "<b>AIPet v1.0</b><br>"
            "An interactive AI desktop pet featuring multi-modal screen analysis, "
            "NVIDIA NIM vision model integration, and safe desktop automation.<br><br>"
            "Created for Windows."
        )
