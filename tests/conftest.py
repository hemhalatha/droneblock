import pytest
from droneblock.core.connector import BaseConnector


class MockConnector(BaseConnector):
    """Shared dummy connector for testing."""

    def connect(self):
        pass

    def send_command(self, command, **params):
        pass

    def arm(self):
        pass

    def disarm(self):
        pass

    def goto(self, lat, lon, alt):
        pass

    def set_mode(self, mode_name: str):
        pass

    def close(self):
        pass
