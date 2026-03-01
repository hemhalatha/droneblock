import unittest
import time
from unittest.mock import MagicMock
from droneblock.core.drone import Drone
from droneblock.actions.base import Action
from droneblock.core.exceptions import ActionTimeoutError, DroneblockError
from droneblock.core.events import EventEmitter
from .conftest import MockConnector


class MockAction(Action):
    def __init__(self, timeout=None, duration=0.5):
        super().__init__(timeout=timeout)
        self.duration = duration
        self.start_called = False
        self.ticks = 0
        self.finished = False

    def start(self):
        self.start_called = True
        self.start_time = time.time()

    def tick(self):
        self.ticks += 1
        if time.time() - self.start_time >= self.duration:
            self.finished = True

    def complete(self):
        return self.finished


class TestMissionExecutor(unittest.TestCase):
    def setUp(self):
        self.events = EventEmitter()
        self.connector = MockConnector("mock://", self.events)
        self.drone = Drone(self.connector)

    def test_action_success(self):
        """Test that a normal action completes successfully."""
        action = MockAction(duration=0.2)
        self.drone.execute(action, blocking=True)
        self.assertTrue(action.finished)
        self.assertGreater(action.ticks, 0)

    def test_action_timeout(self):
        """Test that an action raises ActionTimeoutError when it exceeds timeout."""
        # Action needs 0.5s but timeout is 0.2s
        action = MockAction(timeout=0.2, duration=0.5)

        start_time = time.time()
        with self.assertRaises(ActionTimeoutError):
            self.drone.execute(action, blocking=True)

        elapsed = time.time() - start_time
        self.assertLess(elapsed, 0.5)  # Should have failed earlier
        self.assertTrue(action.aborted)

    def test_events_emitted(self):
        """Test that action.started and action.timeout events are emitted."""
        started_call = MagicMock()
        timeout_call = MagicMock()

        self.drone.on("action.started", started_call)
        self.drone.on("action.timeout", timeout_call)

        # Test start event
        action1 = MockAction(duration=0.1)
        self.drone.execute(action1, blocking=True)
        started_call.assert_called_with(action1)

        # Test timeout event
        action2 = MockAction(timeout=0.1, duration=0.3)
        try:
            self.drone.execute(action2, blocking=True)
        except ActionTimeoutError:
            pass

        timeout_call.assert_called_with(action2)

    def test_invalid_timeout(self):
        """Test that initializing an action with invalid timeout raises ValueError."""
        with self.assertRaises(ValueError):
            MockAction(timeout=-1)
        with self.assertRaises(ValueError):
            MockAction(timeout=0)


if __name__ == "__main__":
    unittest.main()
