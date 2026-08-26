"""NVIDIA NIM API non-blocking async client using PySide6 QThread."""

import json
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
from PySide6.QtCore import QThread, Signal
from app.core.config import get_config
from app.core.logger import logger
from app.core.exceptions import AIClientError
from app.ai.vision import VisionPromptBuilder
from app.ai.tools import ActionPlanner

class AIRequestWorker(QThread):
    """Worker thread for non-blocking HTTP requests to NVIDIA NIM API."""

    response_received = Signal(str, list) # (text_response, actions)
    error_occurred = Signal(str)          # error message

    def __init__(
        self,
        messages: List[Dict[str, Any]],
        image_path: Optional[Path] = None,
        parent=None
    ):
        super().__init__(parent)
        self.messages = messages
        self.image_path = image_path

    def run(self):
        config = get_config()
        api_key = config.get("nvidia_api_key", "").strip()
        endpoint = config.get("api_endpoint", "https://integrate.api.nvidia.com/v1").rstrip("/")
        model = config.get("model_name", "meta/llama-3.2-11b-vision-instruct")
        temperature = float(config.get("temperature", 0.7))
        max_tokens = int(config.get("max_tokens", 1024))

        if not api_key:
            self.error_occurred.emit(
                "NVIDIA NIM API key is not configured. Please set your API key in Settings."
            )
            return

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Build final payload
        payload = {
            "model": model,
            "messages": self.messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        url = f"{endpoint}/chat/completions"
        logger.info(f"Sending request to NVIDIA NIM ({model}) at {url}")

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=45)

            if response.status_code == 401:
                self.error_occurred.emit("Authentication failed: Invalid NVIDIA API key.")
                return
            elif response.status_code == 429:
                self.error_occurred.emit("Rate limit exceeded. Please wait a moment before trying again.")
                return
            elif response.status_code != 200:
                self.error_occurred.emit(
                    f"API Error ({response.status_code}): {response.text[:200]}"
                )
                return

            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                self.error_occurred.emit("Received empty response from AI model.")
                return

            content = choices[0].get("message", {}).get("content", "")
            actions = ActionPlanner.parse_actions_from_text(content)

            logger.info("Successfully received response from NVIDIA NIM.")
            self.response_received.emit(content, actions)

        except requests.exceptions.Timeout:
            logger.error("NVIDIA NIM API request timed out.")
            self.error_occurred.emit("AI request timed out. Please check your network connection.")
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Network error during AI request: {req_err}")
            self.error_occurred.emit(f"Network error: {req_err}")
        except Exception as e:
            logger.error(f"Unexpected error in AI worker: {e}")
            self.error_occurred.emit(f"Unexpected error: {e}")


class AIClient:
    """High-level client managing AI calls and conversation thread creation."""

    def __init__(self):
        self._current_worker: Optional[AIRequestWorker] = None

    def send_message(
        self,
        messages: List[Dict[str, Any]],
        image_path: Optional[Path] = None,
        on_success=None,
        on_error=None
    ) -> AIRequestWorker:
        """
        Spawns non-blocking worker thread for AI completion.
        """
        # Cancel previous worker if still running
        if self._current_worker and self._current_worker.isRunning():
            self._current_worker.terminate()
            self._current_worker.wait()

        worker = AIRequestWorker(messages, image_path=image_path)

        if on_success:
            worker.response_received.connect(on_success)
        if on_error:
            worker.error_occurred.connect(on_error)

        self._current_worker = worker
        worker.start()
        return worker
