import unittest
from unittest.mock import MagicMock
from droneblock.core.drone import Drone
from droneblock.core.events import EventEmitter
from droneblock.core.state import DroneState
from droneblock.core.connector import BaseConnector

class MockConnector(BaseConnector):
    def connect(self): pass
    def send_command(self, command, **params): pass
    def arm(self): pass
    def disarm(self): pass
    def set_mode(self, mode_name: str): pass
    def close(self): pass

class TestDrone(unittest.TestCase):
    def setUp(self):
        # We use a mock or a connected instance via factory
        self.events = EventEmitter()
        self.connector = MockConnector("udp://:14540", self.events)
        self.drone = Drone(self.connector)
        
    def test_initial_state(self):
        self.assertIsInstance(self.drone.events, EventEmitter)
        self.assertIsInstance(self.drone.state, DroneState)
        self.assertFalse(self.drone.state.vehicle_status.armed)

    def test_event_emission(self):
        mock_handler = MagicMock()
        self.drone.on("test_event", mock_handler)
        self.drone.events.emit("test_event", "data")
        mock_handler.assert_called_once_with("data")

if __name__ == "__main__":
    unittest.main()
