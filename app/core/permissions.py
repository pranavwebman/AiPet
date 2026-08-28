"""Permissions manager for desktop automation security."""

from enum import Enum
from typing import Dict, Any, Tuple
from app.core.config import get_config
from app.core.logger import logger

class ActionCategory(Enum):
    READ = "read"                      # Screenshot, active window info, OCR (Safe)
    SAFE_INTERACTION = "safe"          # Mouse move, scroll, select text
    CONSEQUENTIAL = "consequential"    # Typing, clicking submit/delete, closing windows, running commands
    DANGEROUS = "dangerous"            # Arbitrary shell commands, registry modifications (Always reject)

class PermissionManager:
    """Manages permissions and confirmation logic for computer interactions."""

    BLOCKED_ACTION_TYPES = {
        "shell_command",
        "disable_security",
        "edit_registry",
        "raw_python_eval"
    }

    READ_ACTION_TYPES = {
        "capture_screen",
        "get_active_window",
        "perform_ocr",
        "get_cursor_position"
    }

    SAFE_ACTION_TYPES = {
        "move_mouse",
        "scroll"
    }

    CONSEQUENTIAL_ACTION_TYPES = {
        "click",
        "double_click",
        "right_click",
        "type_text",
        "press_key",
        "hotkey",
        "focus_window",
        "close_window"
    }

    @classmethod
    def categorize_action(cls, action: Dict[str, Any]) -> ActionCategory:
        action_type = action.get("type", "").lower()
        if action_type in cls.BLOCKED_ACTION_TYPES:
            return ActionCategory.DANGEROUS
        elif action_type in cls.READ_ACTION_TYPES:
            return ActionCategory.READ
        elif action_type in cls.SAFE_ACTION_TYPES:
            return ActionCategory.SAFE_INTERACTION
        elif action_type in cls.CONSEQUENTIAL_ACTION_TYPES:
            return ActionCategory.CONSEQUENTIAL
        else:
            # Default unknown actions to CONSEQUENTIAL for safety
            return ActionCategory.CONSEQUENTIAL

    @classmethod
    def check_permission(cls, action: Dict[str, Any]) -> Tuple[bool, bool, str]:
        """
        Check if an action is permitted.
        Returns tuple: (is_allowed, requires_user_confirmation, reason)
        """
        config = get_config()
        if not config.get("enable_computer_control", True):
            return False, False, "Computer control is disabled in settings."

        category = cls.categorize_action(action)
        if category == ActionCategory.DANGEROUS:
            logger.warning(f"Rejected dangerous action: {action}")
            return False, False, "This action is prohibited for security reasons."

        if category == ActionCategory.READ:
            return True, False, "Read-only operations require no confirmation."

        if category == ActionCategory.SAFE_INTERACTION:
            confirmation_level = config.get("confirmation_level", "consequential")
            if confirmation_level == "all":
                return True, True, "Confirmation required for all interactions."
            return True, False, "Safe interaction permitted."

        if category == ActionCategory.CONSEQUENTIAL:
            require_confirm = config.get("require_confirmation", True)
            if require_confirm:
                return True, True, "Consequential computer action requires confirmation."
            return True, False, "Consequential action permitted by user settings."

        return False, False, "Action denied."
