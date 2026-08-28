"""Custom exception definitions for AIPet application."""

class AIPetError(Exception):
    """Base exception class for AIPet errors."""
    pass

class ConfigurationError(AIPetError):
    """Exception raised for configuration errors."""
    pass

class AIClientError(AIPetError):
    """Exception raised for AI service communications."""
    pass

class VisionError(AIPetError):
    """Exception raised for screen capture or vision processing failures."""
    pass

class AutomationError(AIPetError):
    """Exception raised for desktop automation failures."""
    pass

class ActionRejectedError(AIPetError):
    """Exception raised when an action is rejected or cancelled by permission manager."""
    pass

class DatabaseError(AIPetError):
    """Exception raised for database operations."""
    pass
