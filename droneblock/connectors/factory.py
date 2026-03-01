"""
DroneBlock Connectors Factory Module.

Provides dynamic instantiation of the appropriate connector backend.
"""

from typing import TYPE_CHECKING, cast
from .pymavlink_connector import PymavlinkConnector
from .dronekit_connector import DroneKitConnector
from .mavsdk_connector import MavsdkConnector
from ..core.exceptions import ConnectionError as DroneConnectionError

if TYPE_CHECKING:
    from ..core.events import EventEmitter
    from ..core.connector import BaseConnector


class ConnectorFactory:
    """Factory for instantiating the appropriate vehicle communication backend.

    The factory analyzes the connection URL schema to determine which
    specialized connector (Pymavlink, DroneKit, or MAVSDK) should be used.
    """

    @staticmethod
    def get_connector(url: str, event_bus: "EventEmitter") -> "BaseConnector":
        """Retrieves an uninitialized connector instance based on the URL.

        Args:
            url: Connection string (e.g., 'udp:127.0.0.1:14550', 'mavsdk:127.0.0.1:50051').
            event_bus: The EventEmitter instance for the vehicle.

        Returns:
            An instance of a class that inherits from BaseConnector.

        Raises:
            ConnectionError: If the URL prefix does not match any known engine.
        """
        # pylint: disable=abstract-class-instantiated
        if url.startswith(("udp:", "tcp:", "serial:")):
            return PymavlinkConnector(url, event_bus)
        if url.startswith("dronekit:"):
            # Ensure it conforms to type system while abstract methods exist
            return cast(
                "BaseConnector", DroneKitConnector(url, event_bus)
            )
        if url.startswith("mavsdk:"):
            return cast(
                "BaseConnector", MavsdkConnector(url, event_bus)
            )

        raise DroneConnectionError(
            f"Unsupported connection scheme: '{url}'. "
            "Supported schemes: udp:, tcp:, serial:, dronekit:, mavsdk:."
        )
