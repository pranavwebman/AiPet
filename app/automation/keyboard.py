"""Keyboard control implementation for Windows using SendInput/keybd_event."""

import sys
import time
import ctypes
from typing import List, Union
from app.core.logger import logger

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    user32 = ctypes.windll.user32

# Virtual key map for common keys
KEY_MAP = {
    "backspace": 0x08,
    "tab": 0x09,
    "enter": 0x0D,
    "shift": 0x10,
    "ctrl": 0x11,
    "alt": 0x12,
    "pause": 0x13,
    "capslock": 0x14,
    "esc": 0x1B,
    "space": 0x20,
    "pageup": 0x21,
    "pagedown": 0x22,
    "end": 0x23,
    "home": 0x24,
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
    "delete": 0x2E,
    "win": 0x5B,
}

# Add 0-9 and A-Z
for i in range(10):
    KEY_MAP[str(i)] = 0x30 + i
for i in range(26):
    char = chr(ord('a') + i)
    KEY_MAP[char] = 0x41 + i

class KeyboardController:
    """Handles programmatic typing, key presses, and hotkey combinations."""

    KEYEVENTF_EXTENDEDKEY = 0x0001
    KEYEVENTF_KEYUP = 0x0002
    KEYEVENTF_UNICODE = 0x0004

    @classmethod
    def type_text(cls, text: str, interval: float = 0.01) -> bool:
        """Type string into focused control character by character."""
        if not text:
            return True

        try:
            if IS_WINDOWS:
                for char in text:
                    # Unicode input
                    user32.keybd_event(0, ord(char), cls.KEYEVENTF_UNICODE, 0)
                    user32.keybd_event(0, ord(char), cls.KEYEVENTF_UNICODE | cls.KEYEVENTF_KEYUP, 0)
                    time.sleep(interval)
            logger.info(f"Typed text: '{text[:20]}...'")
            return True
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            return False

    @classmethod
    def press_key(cls, key_name: str) -> bool:
        """Press and release a single key by name."""
        k = key_name.lower()
        vk = KEY_MAP.get(k)
        if vk is None and len(k) == 1:
            vk = ord(k.upper())

        if vk is None:
            logger.error(f"Unknown key name: {key_name}")
            return False

        try:
            if IS_WINDOWS:
                user32.keybd_event(vk, 0, 0, 0)
                time.sleep(0.05)
                user32.keybd_event(vk, 0, cls.KEYEVENTF_KEYUP, 0)
            logger.info(f"Pressed key: {key_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to press key {key_name}: {e}")
            return False

    @classmethod
    def hotkey(cls, keys: List[str]) -> bool:
        """Execute hotkey sequence (e.g. ['ctrl', 'c'])."""
        if not keys:
            return True

        vks = []
        for key in keys:
            k = key.lower()
            vk = KEY_MAP.get(k)
            if vk is None and len(k) == 1:
                vk = ord(k.upper())
            if vk is not None:
                vks.append(vk)

        if not vks:
            logger.error(f"No valid virtual keys in hotkey list: {keys}")
            return False

        try:
            if IS_WINDOWS:
                # Press all keys in sequence
                for vk in vks:
                    user32.keybd_event(vk, 0, 0, 0)
                    time.sleep(0.02)

                time.sleep(0.05)

                # Release all keys in reverse sequence
                for vk in reversed(vks):
                    user32.keybd_event(vk, 0, cls.KEYEVENTF_KEYUP, 0)
                    time.sleep(0.02)

            logger.info(f"Executed hotkey: {keys}")
            return True
        except Exception as e:
            logger.error(f"Failed to execute hotkey {keys}: {e}")
            return False
