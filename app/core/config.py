"""Path utilities and configuration management for AIPet."""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

APP_NAME = "AIPet"

def get_base_dir() -> Path:
    """Return base directory for bundled assets or source root."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent.parent

def get_user_data_dir() -> Path:
    """Return persistent user application data directory."""
    if sys.platform == "win32":
        base_appdata = os.environ.get("APPDATA")
        if base_appdata:
            data_dir = Path(base_appdata) / APP_NAME
        else:
            data_dir = Path.home() / "AppData" / "Roaming" / APP_NAME
    else:
        data_dir = Path.home() / ".config" / APP_NAME

    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def get_config_dir() -> Path:
    config_dir = get_user_data_dir() / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def get_logs_dir() -> Path:
    logs_dir = get_user_data_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir

def get_db_dir() -> Path:
    db_dir = get_user_data_dir() / "data"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir

def get_cache_dir() -> Path:
    cache_dir = get_user_data_dir() / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir

def get_assets_dir() -> Path:
    return get_base_dir() / "app" / "assets"


DEFAULT_CONFIG: Dict[str, Any] = {
    # General
    "start_with_windows": False,
    "always_on_top": True,
    "pet_x": 100,
    "pet_y": 100,
    "enable_animations": True,
    "enable_sounds": False,
    "global_hotkey": "Ctrl+Alt+Space",

    # AI
    "ai_provider": "NVIDIA NIM",
    "nvidia_api_key": "",
    "model_name": "meta/llama-3.2-11b-vision-instruct",
    "api_endpoint": "https://integrate.api.nvidia.com/v1",
    "temperature": 0.7,
    "max_tokens": 1024,
    "system_prompt": "You are AIPet, a friendly, helpful, and playful desktop AI assistant living on the user's screen. Keep responses concise, helpful, and personable unless detailed analysis is requested.",

    # Screen
    "enable_screen_analysis": True,
    "analyze_active_window_only": False,
    "enable_ocr": True,

    # Automation
    "enable_computer_control": True,
    "require_confirmation": True,
    "confirmation_level": "consequential", # 'none', 'consequential', 'all'

    # Memory
    "enable_memory": True,
    "max_context_messages": 20
}

class Config:
    def __init__(self, config_path: Path = None):
        if config_path is None:
            config_path = get_config_dir() / "settings.json"
        self.config_path = config_path
        self._data: Dict[str, Any] = dict(DEFAULT_CONFIG)
        self.load()

    def load(self) -> None:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self._data.update(loaded)
            except Exception as e:
                print(f"Failed to load config, using defaults: {e}", file=sys.stderr)

    def save(self) -> None:
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}", file=sys.stderr)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self.save()

    def update(self, new_data: Dict[str, Any]) -> None:
        self._data.update(new_data)
        self.save()

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)

# Singleton global instance
_config_instance = None

def get_config() -> Config:
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
