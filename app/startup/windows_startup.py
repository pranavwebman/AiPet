"""Windows startup registry management module."""

import sys
from app.core.config import APP_NAME
from app.core.logger import logger

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import winreg

REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

class WindowsStartupManager:
    """Manages adding/removing AIPet from Windows registry startup."""

    @staticmethod
    def get_executable_path() -> str:
        """Returns executable or python command path."""
        if getattr(sys, 'frozen', False):
            return f'"{sys.executable}"'
        else:
            main_script = sys.argv[0]
            return f'"{sys.executable}" "{main_script}"'

    @classmethod
    def set_startup(cls, enable: bool) -> bool:
        """Enable or disable startup registration in Windows Registry."""
        if not IS_WINDOWS:
            logger.info("Startup manager called on non-Windows OS; ignoring.")
            return False

        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                REG_PATH,
                0,
                winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE
            )
            if enable:
                cmd = cls.get_executable_path()
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
                logger.info(f"Registered Windows startup entry: {APP_NAME} -> {cmd}")
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                    logger.info(f"Removed Windows startup entry: {APP_NAME}")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
            return True
        except Exception as e:
            logger.error(f"Failed to modify startup registry: {e}")
            return False

    @classmethod
    def is_startup_enabled(cls) -> bool:
        """Check if startup entry exists in Windows Registry."""
        if not IS_WINDOWS:
            return False

        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                REG_PATH,
                0,
                winreg.KEY_READ
            )
            try:
                val, _ = winreg.QueryValueEx(key, APP_NAME)
                winreg.CloseKey(key)
                return bool(val)
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except Exception as e:
            logger.error(f"Failed to read startup registry: {e}")
            return False
