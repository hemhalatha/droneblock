import logging
from typing import Callable, Dict, List, Any

log = logging.getLogger("droneblock.events")

class EventEmitter:
    """Internal event bus for droneblock.

    Supports uORB-style topics and raw MAVLink messages for internal 
    communication and user-defined event handling.
    """
    def __init__(self) -> None:
        """Initializes the EventEmitter with an empty handler map."""
        self._handlers: Dict[str, List[Callable[..., Any]]] = {}

    def on(self, event_name: str, handler: Callable[..., Any]) -> None:
        """Subscribes a handler to a specific topic.

        Args:
            event_name: The name of the event to subscribe to.
            handler: A callback function to be executed when the event is emitted.
        """
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        self._handlers[event_name].append(handler)

    def emit(self, event_name: str, data: Any = None) -> None:
        """Publishes an event to all registered subscribers.

        Args:
            event_name: The name of the event to publish.
            data: Optional payload to pass to the handlers.
        """
        if event_name in self._handlers:
            for handler in self._handlers[event_name]:
                try:
                    handler(data)
                except Exception as e:
                    log.error(f"Error in handler for '{event_name}': {e}", exc_info=True)

class GlobalBus:
    """Singleton access to a global event bus.

    Note:
        Prefer using the instance-bound event bus in the Drone class 
        over this global singleton for better testability and isolation.
    """
    _instance: 'EventEmitter' = None

    @classmethod
    def get(cls) -> 'EventEmitter':
        """Returns the singleton EventEmitter instance."""
        if cls._instance is None:
            cls._instance = EventEmitter()
        return cls._instance
