from ..core.connector import BaseConnector

class DroneKitConnector(BaseConnector):
    """
    Placeholder for DroneKit-based connector.
    Useful for legacy installations or specific ArduPilot features.
    """
    def connect(self):
        raise NotImplementedError("DroneKitConnector not implemented in V1.0")

    def send_command(self, command: int, **params):
        pass

    def set_mode(self, mode_name: str):
        pass

    def close(self):
        pass
