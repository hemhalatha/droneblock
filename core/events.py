import time
from typing import Callable, Dict, List, Any

class EventEmitter:
    """
    Internal event bus for droneblock.
    Supports uORB-style topics and raw MAVLink messages.
    """
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}

    def on(self, event_name: str, handler: Callable):
        """Subscribe to a topic."""
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)

    def emit(self, event_name: str, data: Any = None):
        """Publish an event to all subscribers."""
        if event_name in self._handlers:
            for handler in self._handlers[event_name]:
                try:
                    handler(data)
                except Exception as e:
                    # In production, we'd log this properly
                    print(f"[EventEmitter] Error in handler for {event_name}: {e}")

class GlobalBus:
    """Singleton-like access for the main event bus if needed."""
    _instance = None
    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = EventEmitter()
        return cls._instance
