"""Central event bus using PySide6 signals."""

from PySide6.QtCore import QObject, Signal

class EventBus(QObject):
    """Global application signal bus for decoupled component communication."""

    # Pet state and animation
    pet_state_changed = Signal(str)            # new state name (e.g. 'happy', 'thinking')
    pet_message_spoken = Signal(str)           # message text
    pet_position_changed = Signal(int, int)    # x, y

    # Chat & AI interactions
    chat_requested = Signal()                  # open/focus chat window
    screen_analysis_requested = Signal()       # trigger screen capture & analysis
    user_message_sent = Signal(str)            # message text
    ai_response_received = Signal(str)         # response text
    ai_error_occurred = Signal(str)            # error description

    # Automation & Permissions
    action_confirmation_requested = Signal(dict) # action payload dictionary
    action_confirmed = Signal(str)             # action_id
    action_cancelled = Signal(str)             # action_id

    # Settings & System
    settings_changed = Signal()                # emitted when settings updated
    pause_pet_toggled = Signal(bool)           # True if paused
    exit_requested = Signal()                  # trigger app exit

_event_bus_instance = None

def get_event_bus() -> EventBus:
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus()
    return _event_bus_instance
