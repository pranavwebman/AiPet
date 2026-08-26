"""Pet autonomous behavior and idle state manager."""

import random
from PySide6.QtCore import QObject, QTimer
from app.core.config import get_config
from app.pet.animation import PetAnimationEngine
from app.core.logger import logger

class PetBehaviorController(QObject):
    """Triggers occasional idle expressions or animations when pet is idle."""

    def __init__(self, animation_engine: PetAnimationEngine, parent=None):
        super().__init__(parent)
        self.anim = animation_engine
        self.is_paused = False

        self._timer = QTimer(self)
        self._timer.setInterval(15000) # Check every 15 seconds
        self._timer.timeout.connect(self._on_idle_tick)
        self._timer.start()

    def set_paused(self, paused: bool) -> None:
        self.is_paused = paused
        if paused:
            self.anim.set_state("sleeping")
        else:
            self.anim.set_state("idle")

    def _on_idle_tick(self) -> None:
        if self.is_paused or self.anim.current_state != "idle":
            return

        config = get_config()
        if not config.get("enable_animations", True):
            return

        # Random idle flavor action (15% chance)
        r = random.random()
        if r < 0.15:
            idle_state = random.choice(["happy", "confused"])
            logger.debug(f"Triggering idle flavor animation: {idle_state}")
            self.anim.set_state(idle_state, duration_ms=2500)
