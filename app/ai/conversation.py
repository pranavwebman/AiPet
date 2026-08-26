"""Conversation manager coordinating history, system instructions, and AI requests."""

from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from app.core.config import get_config
from app.core.events import get_event_bus
from app.memory.conversation_store import ConversationStore
from app.ai.client import AIClient
from app.ai.vision import VisionPromptBuilder
from app.ai.tools import ActionPlanner
from app.core.logger import logger

class ConversationManager:
    """Manages chat context formatting, memory saving, and AI completion dispatch."""

    def __init__(self, conversation_store: Optional[ConversationStore] = None):
        self.store = conversation_store if conversation_store else ConversationStore()
        self.client = AIClient()
        self.event_bus = get_event_bus()

    def process_user_message(
        self,
        text_prompt: str,
        image_path: Optional[Path] = None,
        on_response: Optional[Callable[[str, list], None]] = None,
        on_error: Optional[Callable[[str], None]] = None
    ):
        """Builds payload, persists user message, and sends query to AI Client."""
        config = get_config()

        # 1. Store user message in local SQLite DB if memory enabled
        if config.get("enable_memory", True):
            self.store.add_message("user", text_prompt, image_path=str(image_path) if image_path else None)

        # 2. Build full message list with system prompt and history
        messages = self._build_messages_payload(text_prompt, image_path)

        # 3. Define internal callbacks to save response and emit events
        def handle_success(response_text: str, actions: list):
            if config.get("enable_memory", True):
                self.store.add_message("assistant", response_text)
            if on_response:
                on_response(response_text, actions)
            else:
                self.event_bus.ai_response_received.emit(response_text)

        def handle_error(err_msg: str):
            if on_error:
                on_error(err_msg)
            else:
                self.event_bus.ai_error_occurred.emit(err_msg)

        # 4. Dispatch request non-blockingly
        self.client.send_message(
            messages,
            image_path=image_path,
            on_success=handle_success,
            on_error=handle_error
        )

    def _build_messages_payload(
        self, current_prompt: str, image_path: Optional[Path] = None
    ) -> List[Dict[str, Any]]:
        config = get_config()
        messages: List[Dict[str, Any]] = []

        # System Prompt
        sys_prompt = config.get("system_prompt", "")
        if config.get("enable_computer_control", True):
            sys_prompt += ActionPlanner.build_system_action_instructions()

        messages.append({"role": "system", "content": sys_prompt})

        # History context
        if config.get("enable_memory", True):
            limit = int(config.get("max_context_messages", 20))
            recent_msgs = self.store.get_recent_messages(limit=limit)
            for m in recent_msgs:
                # Omit images from old context to save bandwidth/tokens
                messages.append({
                    "role": m["role"],
                    "content": m["content"]
                })

        # Current User Turn
        if image_path and image_path.exists():
            vision_content = VisionPromptBuilder.build_vision_message(current_prompt, image_path)
            messages.append({"role": "user", "content": vision_content})
        else:
            messages.append({"role": "user", "content": current_prompt})

        return messages
