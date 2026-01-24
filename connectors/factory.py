from typing import TYPE_CHECKING
from .pymavlink_connector import PymavlinkConnector
from .dronekit_connector import DroneKitConnector
from .mavsdk_connector import MavsdkConnector
from ..core.exceptions import ConnectionError

if TYPE_CHECKING:
    from ..core.events import EventEmitter
    from ..core.connector import BaseConnector

class ConnectorFactory:
    """Factory for instantiating the appropriate vehicle communication backend.

    The factory analyzes the connection URL schema to determine which 
    specialized connector (Pymavlink, DroneKit, or MAVSDK) should be used.
    """

    @staticmethod
    def get_connector(url: str, event_bus: 'EventEmitter') -> 'BaseConnector':
        """Retrieves an uninitialized connector instance based on the URL.

        Args:
            url: Connection string (e.g., 'udp:127.0.0.1:14550', 'mavsdk:127.0.0.1:50051').
            event_bus: The EventEmitter instance for the vehicle.

        Returns:
            An instance of a class that inherits from BaseConnector.

        Raises:
            ConnectionError: If the URL prefix does not match any known engine.
        """
        if url.startswith(("udp:", "tcp:", "serial:")):
            return PymavlinkConnector(url, event_bus)
        elif url.startswith("dronekit:"):
            return DroneKitConnector(url, event_bus)
        elif url.startswith("mavsdk:"):
            return MavsdkConnector(url, event_bus)
        else:
            raise ConnectionError(
                f"Unsupported connection scheme: '{url}'. "
                "Supported schemes: udp:, tcp:, serial:, dronekit:, mavsdk:."
            )
