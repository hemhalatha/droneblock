"""
DroneBlock Core Drone Interface Module.

Serves as the primary entry point for controlling a vehicle.
"""
from typing import Any, Optional, Union, TYPE_CHECKING
import threading

from .events import EventEmitter
from .state import DroneState
from ..telemetry.mapping import TelemetryMapper
from .logger import get_logger
from .connector import BaseConnector

if TYPE_CHECKING:
    from ..mission.executor import Mission
    from ..actions.base import Action
    from ..connectors.factory import ConnectorFactory
    from ..mission.executor import MissionExecutor

log = get_logger("core.drone")

class Drone:
    """Standard interface for drone control in the DroneBlock ecosystem.

    This class serves as the primary entry point for developers, coordinating
    hardware communication (via Connectors), mission execution, and telemetry 
    processing.

    Attributes:
        events (EventEmitter): The event bus for asynchronous notifications.
        state (DroneState): Real-time normalized state of the vehicle.
        connector (BaseConnector): The active communication backend.
        mapper (TelemetryMapper): Internal engine mapping raw data to state.
        current_action (Optional[Action]): The currently executing action, if any.
    """

    def __init__(self, connector: BaseConnector):
        """Initializes the Drone with a pre-configured connector.

        Args:
            connector: An instance of a BaseConnector subclass.
        """
        self.events = connector.events
        self.state = DroneState()
        self.connector = connector

        # Setup telemetry mapping
        self.mapper = TelemetryMapper(self.events, self.state)
        self.current_action: Optional[Any] = None

    @classmethod
    def connect(cls, url: str) -> 'Drone':
        """Factory method to establish a connection to a vehicle.

        Args:
            url: Connection string (e.g., 'udp:127.0.0.1:14540', 'serial:///dev/ttyUSB0:57600').

        Returns:
            A connected and ready-to-use Drone instance.
        """
        # pylint: disable=import-outside-toplevel
        from ..connectors.factory import ConnectorFactory

        # Create a shared event bus for the new drone instance
        events = EventEmitter()

        # Instantiate the appropriate connector via factory
        connector = ConnectorFactory.get_connector(url, events)
        connector.connect()

        return cls(connector)

    def on(self, topic: str, handler: Any) -> None:
        """Registers a callback for a specific event topic.

        Args:
            topic: The event identifier (e.g., 'vehicle_gps_position').
            handler: Callable function to execute on event emission.
        """
        self.events.on(topic, handler)

    def execute(
        self, mission_or_action: Union['Mission', 'Action'], blocking: bool = True
    ) -> Optional[threading.Thread]:
        """Runs a task or a sequence of tasks on the vehicle.

        Args:
            mission_or_action: An individual Action or a Mission sequence.
            blocking: If True, waits for completion. If False, runs in background.

        Returns:
            The execution Thread if non-blocking, else None.
        """
        # pylint: disable=import-outside-toplevel
        from ..mission.executor import MissionExecutor
        executor = MissionExecutor(self)
        return executor.run(mission_or_action, blocking=blocking)

    def arm(self) -> None:
        """Sends an arming command to the vehicle."""
        log.info("Requesting vehicle arm...")
        self.connector.arm()

    def disarm(self) -> None:
        """Sends a disarming command to the vehicle."""
        log.info("Requesting vehicle disarm...")
        self.connector.disarm()

    def set_mode(self, mode: str) -> None:
        """Switches the vehicle to a specific flight mode.

        Args:
            mode: The target mode name (e.g., 'GUIDED', 'AUTO', 'STABILIZE').
        """
        log.info("Switching vehicle mode to: %s", mode)
        self.connector.set_mode(mode)

    def close(self) -> None:
        """Gracefully shuts down the connector and cleans up resources."""
        log.info("Closing drone connection and cleaning up...")
        self.connector.close()

    def __repr__(self) -> str:
        return f"Drone(url={self.connector.url}, nav_state={self.state.vehicle_status.nav_state})"
