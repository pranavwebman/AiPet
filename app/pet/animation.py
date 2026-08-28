"""State-based animation engine for desktop pet."""

from typing import Dict, Optional
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtGui import QPixmap, QIcon
from app.core.config import get_assets_dir
from app.core.logger import logger

class PetAnimationEngine(QObject):
    """Manages animation states, frame loading, and automatic state resets."""

    state_changed = Signal(str, QPixmap) # (state_name, pixmap)

    VALID_STATES = [
        "idle",
        "hover",
        "clicked",
        "thinking",
        "talking",
        "happy",
        "confused",
        "error",
        "sleeping"
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_state = "idle"
        self._pixmaps: Dict[str, QPixmap] = {}
        self._load_assets()

        # Timer to reset transient states back to idle
        self._reset_timer = QTimer(self)
        self._reset_timer.setSingleShot(True)
        self._reset_timer.timeout.connect(self._on_reset_timeout)

    def _load_assets(self) -> None:
        assets_dir = get_assets_dir()
        for state in self.VALID_STATES:
            path = assets_dir / f"pet_{state}.png"
            if path.exists():
                pix = QPixmap(str(path))
                self._pixmaps[state] = pix
            else:
                logger.warning(f"Asset file missing for state {state}: {path}")

    def set_state(self, state: str, duration_ms: Optional[int] = None) -> None:
        """
        Transition pet to a new animation state.
        Optionally set duration in ms before returning to 'idle'.
        """
        if state not in self.VALID_STATES:
            logger.warning(f"Invalid animation state requested: {state}")
            return

        self.current_state = state
        logger.debug(f"Pet animation state set to: {state}")

        pixmap = self._pixmaps.get(state) or self._pixmaps.get("idle")
        if pixmap:
            self.state_changed.emit(state, pixmap)

        # Handle transient state reset timer
        self._reset_timer.stop()
        if duration_ms and duration_ms > 0 and state != "idle":
            self._reset_timer.start(duration_ms)

    def _on_reset_timeout(self) -> None:
        if self.current_state not in ("sleeping", "idle"):
            self.set_state("idle")

    def get_current_pixmap(self) -> QPixmap:
        return self._pixmaps.get(self.current_state) or QPixmap()
