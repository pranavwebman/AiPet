"""Unit tests for AIPet core modules and persistence."""

import os
import json
import pytest
from pathlib import Path
from app.core.config import Config, DEFAULT_CONFIG
from app.core.permissions import PermissionManager, ActionCategory
from app.memory.database import Database
from app.memory.conversation_store import ConversationStore
from app.ai.tools import ActionPlanner
from app.startup.windows_startup import WindowsStartupManager

@pytest.fixture
def temp_config_path(tmp_path):
    return tmp_path / "test_settings.json"

def test_config_loading_and_saving(temp_config_path):
    config = Config(config_path=temp_config_path)
    assert config.get("model_name") == DEFAULT_CONFIG["model_name"]

    config.set("model_name", "custom/model-v1")
    assert config.get("model_name") == "custom/model-v1"

    # Reload from file
    reloaded = Config(config_path=temp_config_path)
    assert reloaded.get("model_name") == "custom/model-v1"

def test_permission_categorization():
    read_act = {"type": "capture_screen"}
    safe_act = {"type": "move_mouse", "x": 10, "y": 20}
    conseq_act = {"type": "click", "x": 100, "y": 200}
    dangerous_act = {"type": "shell_command"}

    assert PermissionManager.categorize_action(read_act) == ActionCategory.READ
    assert PermissionManager.categorize_action(safe_act) == ActionCategory.SAFE_INTERACTION
    assert PermissionManager.categorize_action(conseq_act) == ActionCategory.CONSEQUENTIAL
    assert PermissionManager.categorize_action(dangerous_act) == ActionCategory.DANGEROUS

def test_permission_check():
    dangerous_act = {"type": "shell_command"}
    is_allowed, req_confirm, reason = PermissionManager.check_permission(dangerous_act)
    assert is_allowed is False

    read_act = {"type": "capture_screen"}
    is_allowed, req_confirm, reason = PermissionManager.check_permission(read_act)
    assert is_allowed is True
    assert req_confirm is False

def test_action_planner_parsing():
    sample_llm_output = """Here is the action you requested:
```json
[
    {"type": "click", "x": 500, "y": 300, "description": "Click Submit button"},
    {"type": "type_text", "text": "Hello World", "description": "Type text"}
]
```"""
    actions = ActionPlanner.parse_actions_from_text(sample_llm_output)
    assert len(actions) == 2
    assert actions[0]["type"] == "click"
    assert actions[0]["x"] == 500
    assert actions[1]["type"] == "type_text"
    assert actions[1]["text"] == "Hello World"

def test_sqlite_conversation_store(tmp_path):
    db_path = tmp_path / "test_aipet.db"
    db = Database(db_path=db_path)
    store = ConversationStore(db=db, session_id="test_session")

    store.add_message("user", "Hello AIPet")
    store.add_message("assistant", "Hello human!")

    msgs = store.get_recent_messages(limit=10)
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[0]["content"] == "Hello AIPet"
    assert msgs[1]["role"] == "assistant"
    assert msgs[1]["content"] == "Hello human!"

    store.clear_history()
    assert len(store.get_recent_messages()) == 0
