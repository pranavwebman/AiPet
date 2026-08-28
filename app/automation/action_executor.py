"""Action Executor module driving mouse, keyboard, and Windows operations."""

from typing import Dict, Any, List, Tuple
from app.core.permissions import PermissionManager, ActionCategory
from app.core.exceptions import ActionRejectedError, AutomationError
from app.core.logger import logger
from app.automation.mouse import MouseController
from app.automation.keyboard import KeyboardController
from app.automation.windows import WindowsAutomation

class ActionExecutor:
    """Validates permissions and executes structured action objects."""

    @classmethod
    def execute_action(cls, action: Dict[str, Any], user_confirmed: bool = False) -> Tuple[bool, str]:
        """
        Check permissions and execute action dictionary.
        Returns (success: bool, message: str)
        """
        is_allowed, req_confirm, reason = PermissionManager.check_permission(action)

        if not is_allowed:
            logger.warning(f"Action blocked: {reason}")
            return False, f"Action blocked: {reason}"

        if req_confirm and not user_confirmed:
            logger.info(f"Action requires user confirmation: {action}")
            return False, "REQUIRES_CONFIRMATION"

        action_type = action.get("type", "").lower()
        logger.info(f"Executing action [{action_type}]: {action.get('description', '')}")

        try:
            if action_type == "move_mouse":
                x = action.get("x", 0)
                y = action.get("y", 0)
                res = MouseController.move(x, y)
                return res, f"Moved mouse to ({x}, {y})"

            elif action_type == "click":
                x = action.get("x")
                y = action.get("y")
                res = MouseController.click(x, y)
                return res, "Clicked mouse"

            elif action_type == "double_click":
                x = action.get("x")
                y = action.get("y")
                res = MouseController.double_click(x, y)
                return res, "Double clicked mouse"

            elif action_type == "right_click":
                x = action.get("x")
                y = action.get("y")
                res = MouseController.right_click(x, y)
                return res, "Right clicked mouse"

            elif action_type == "type_text":
                text = action.get("text", "")
                res = KeyboardController.type_text(text)
                return res, f"Typed text: {text[:20]}..."

            elif action_type == "press_key":
                key = action.get("key", "")
                res = KeyboardController.press_key(key)
                return res, f"Pressed key {key}"

            elif action_type == "hotkey":
                keys = action.get("keys", [])
                res = KeyboardController.hotkey(keys)
                return res, f"Executed hotkey: {keys}"

            elif action_type == "scroll":
                clicks = action.get("clicks", 1)
                res = MouseController.scroll(clicks)
                return res, f"Scrolled wheel by {clicks}"

            elif action_type == "focus_window":
                title = action.get("title", "")
                res = WindowsAutomation.focus_window_by_title(title)
                return res, f"Focused window matching '{title}'"

            elif action_type == "close_window":
                title = action.get("title", "")
                res = WindowsAutomation.close_window_by_title(title)
                return res, f"Closed window matching '{title}'"

            else:
                return False, f"Unsupported action type: {action_type}"

        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            return False, f"Execution failed: {e}"
