from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .events import EventEmitter

class BaseConnector(ABC):
    """Abstract interface for vehicle communication backends.

    Connectors translate high-level commands into backend-specific protocols
    (e.g., MAVLink via pymavlink or MAVSDK) and emit raw telemetry data 
    through the shared event bus.

    Attributes:
        url (str): The connection endpoint (e.g., 'udp:127.0.0.1:14550').
        events (EventEmitter): The event bus for distributing received messages.
    """

    def __init__(self, connection_url: str, events: 'EventEmitter') -> None:
        """Initializes the connector with connection parameters.

        Args:
            connection_url: String identifying the serial or network port.
            events: Shared EventEmitter instance for the vehicle.
        """
        self.url = connection_url
        self.events = events

    @abstractmethod
    def connect(self) -> None:
        """Establishes the hardware or network connection.

        Internal state should transition to connected after successful execution.
        
        Raises:
            ConnectionError: If the backend fails to initialize or connect.
        """
        pass

    @abstractmethod
    def send_command(self, command: int, **params: float) -> None:
        """Dispatches a low-level command to the vehicle.

        Args:
            command: The integer identifier for the command (e.g., MAV_CMD).
            **params: Parameters for the command, typically named p1 through p7.
        """
        pass

    @abstractmethod
    def arm(self) -> None:
        """Requests the vehicle to arm its motors."""
        pass

    @abstractmethod
    def disarm(self) -> None:
        """Requests the vehicle to disarm its motors immediately."""
        pass

    @abstractmethod
    def set_mode(self, mode_name: str) -> None:
        """Instructs the vehicle to transition to a new flight mode.

        Args:
            mode_name: The backend-specific mode string (e.g., 'GUIDED').
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Terminates the connection and performs cleanup of resources."""
        pass
