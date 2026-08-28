"""Desktop pet movement controller."""

from PySide6.QtCore import QObject
from app.core.config import get_config

class PetMovementController(QObject):
    """Manages pet screen position persistence and boundary constraints."""

    @staticmethod
    def save_position(x: int, y: int) -> None:
        config = get_config()
        config.set("pet_x", x)
        config.set("pet_y", y)

    @staticmethod
    def get_saved_position() -> tuple[int, int]:
        config = get_config()
        return (int(config.get("pet_x", 100)), int(config.get("pet_y", 100)))
