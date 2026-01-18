from .pymavlink_connector import PymavlinkConnector
from .dronekit_connector import DroneKitConnector
from .mavsdk_connector import MavsdkConnector
from ..core.exceptions import ConnectionError

class ConnectorFactory:
    """
    Factory to instantiate the appropriate connector based on URL scheme.
    """
    @staticmethod
    def get_connector(url: str, event_bus):
        if url.startswith(("udp://", "tcp:", "serial:")):
            return PymavlinkConnector(url, event_bus)
        elif url.startswith("dronekit:"):
            return DroneKitConnector(url, event_bus)
        elif url.startswith("mavsdk:"):
            return MavsdkConnector(url, event_bus)
        else:
            raise ConnectionError(f"Unsupported connection scheme for URL: {url}")
