"""Structured action models and parsing tools for AI computer interaction."""

import json
import re
from typing import List, Dict, Any, Optional
from app.core.logger import logger

ACTION_JSON_PATTERN = re.compile(r"```json\s*(\[\s*\{.*?\}\s*\])\s*```", re.DOTALL)
INLINE_JSON_PATTERN = re.compile(r"(\[\s*\{\s*\"type\".*?\}\s*\])", re.DOTALL)

class ActionPlanner:
    """Parses and structures tool calls / automation actions from LLM output."""

    VALID_ACTION_TYPES = {
        "move_mouse",
        "click",
        "double_click",
        "right_click",
        "type_text",
        "press_key",
        "hotkey",
        "scroll",
        "focus_window",
        "close_window",
        "capture_screen"
    }

    @classmethod
    def parse_actions_from_text(cls, text: str) -> List[Dict[str, Any]]:
        """
        Extract structured action dictionaries from AI text response.
        Actions should be formatted in JSON blocks inside response text.
        """
        actions: List[Dict[str, Any]] = []
        if not text:
            return actions

        # Try matching ```json [...] ``` block
        match = ACTION_JSON_PATTERN.search(text)
        json_str = None
        if match:
            json_str = match.group(1)
        else:
            match = INLINE_JSON_PATTERN.search(text)
            if match:
                json_str = match.group(1)

        if json_str:
            try:
                raw_list = json.loads(json_str)
                if isinstance(raw_list, list):
                    for item in raw_list:
                        if isinstance(item, dict) and cls.validate_action(item):
                            actions.append(item)
            except Exception as e:
                logger.warning(f"Failed to parse action JSON block from AI response: {e}")

        return actions

    @classmethod
    def validate_action(cls, action: Dict[str, Any]) -> bool:
        """Validate if action object has correct parameters and known type."""
        action_type = action.get("type", "").lower()
        if action_type not in cls.VALID_ACTION_TYPES:
            logger.warning(f"Invalid or unsupported action type: {action_type}")
            return False

        if action_type in ("click", "double_click", "right_click", "move_mouse"):
            x = action.get("x")
            y = action.get("y")
            if x is not None and not isinstance(x, (int, float)):
                return False
            if y is not None and not isinstance(y, (int, float)):
                return False

        if action_type == "type_text":
            if not isinstance(action.get("text"), str):
                return False

        if action_type == "press_key":
            if not isinstance(action.get("key"), str):
                return False

        if action_type == "hotkey":
            keys = action.get("keys")
            if not isinstance(keys, list) or not all(isinstance(k, str) for k in keys):
                return False

        return True

    @classmethod
    def build_system_action_instructions(cls) -> str:
        """Instructions included in system prompt so LLM formats actions strictly."""
        return (
            "\n\nCOMPUTER AUTOMATION CAPABILITIES:\n"
            "If the user asks you to interact with the computer, you may propose actions using a JSON block.\n"
            "Supported Action Types:\n"
            "- click (x, y)\n"
            "- double_click (x, y)\n"
            "- right_click (x, y)\n"
            "- move_mouse (x, y)\n"
            "- type_text (text)\n"
            "- press_key (key)\n"
            "- hotkey (keys: [list of keys])\n"
            "- scroll (clicks)\n"
            "- focus_window (title)\n\n"
            "Format actions as a JSON array inside code fences, for example:\n"
            "```json\n"
            "[\n"
            '  {"type": "click", "x": 500, "y": 300, "description": "Click Submit button"},\n'
            '  {"type": "type_text", "text": "Hello World", "description": "Type into field"}\n'
            "]\n"
            "```\n"
            "Every action must have a brief 'description'."
        )
