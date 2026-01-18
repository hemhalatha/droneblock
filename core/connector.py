from abc import ABC, abstractmethod
from typing import Any

class BaseConnector(ABC):
    """Abstract interface for MAVLink backends (pymavlink, DroneKit, MAVSDK).

    Connectors are responsible for low-level communication with the autopilot.
    They emit raw messages via the event bus and execute basic commands.

    Attributes:
        url (str): Connection string (e.g., 'udp://:14540').
        events (EventEmitter): Shared event bus for message distribution.
    """
    def __init__(self, connection_url: str, events):
        """Initializes the connector.

        Args:
            connection_url: The URL to connect to.
            events: The event emitter instance.
        """
        self.url = connection_url
        self.events = events

    @abstractmethod
    def connect(self):
        """Establishes the connection and starts the receiver loop.

        Raises:
            ConnectionError: If the connection cannot be established.
        """
        pass

    @abstractmethod
    def send_command(self, command: int, **params):
        """Sends a raw MAVLink command to the drone.

        Args:
            command: MAV_CMD identifier.
            **params: Parameters for the MAVLink command (p1 to p7).
        """
        pass

    @abstractmethod
    def arm(self):
        """Arms the drone's motors."""
        pass

    @abstractmethod
    def disarm(self):
        """Disarms the drone's motors."""
        pass

    @abstractmethod
    def set_mode(self, mode_name: str):
        """Sets the flight mode of the drone.

        Args:
            mode_name: The name of the mode to set (e.g., 'GUIDED', 'AUTO').
        """
        pass

    @abstractmethod
    def close(self):
        """Shuts down the connection and stops all threads."""
        pass
