from .events import EventEmitter
from .state import DroneState
from ..telemetry.mapping import TelemetryMapper
from ..core.logger import get_logger
from .connector import BaseConnector

log = get_logger("core.drone")

class Drone:
    """Main user-facing API for droneblock.

    Coordinates events, state, mapping, and the connector.
    Uses dependency injection for the connector to allow for better testability.

    Attributes:
        events (EventEmitter): Event bus for telemetry and status updates.
        state (DroneState): Current state of the vehicle.
        connector (BaseConnector): Backend-specific communication layer.
    """
    def __init__(self, connector: BaseConnector):
        """Initializes the Drone instance.

        Args:
            connector: An instance of a BaseConnector subclass.
        """
        self.events = connector.events
        self.state = DroneState()
        self.connector = connector
        
        # Setup telemetry mapping
        self.mapper = TelemetryMapper(self.events, self.state)
        
        self.current_action = None

    @classmethod
    def connect(cls, url: str) -> 'Drone':
        """Static factory method to create and connect a Drone.

        Args:
            url: Connection string (e.g., 'udp://:14540', 'tcp:127.0.0.1:5760').

        Returns:
            A connected Drone instance.
        """
        from ..connectors.factory import ConnectorFactory
        from .events import EventEmitter
        
        # Create a shared event bus
        events = EventEmitter()
        
        # Instantiate the appropriate connector
        connector = ConnectorFactory.get_connector(url, events)
        connector.connect()
        
        return cls(connector)

    def on(self, topic: str, handler):
        """Subscribes to events on the internal bus.

        Args:
            topic: The event topic name (e.g., 'vehicle_gps_position', 'action.started').
            handler: Callback function for the event.
        """
        self.events.on(topic, handler)

    def execute(self, mission_or_action, blocking: bool = True):
        """Executes an Action or a Mission.

        Args:
            mission_or_action: The sequence or atomic behavior to run.
            blocking: If True, waits for completion. If False, runs in a daemon thread.

        Returns:
            The execution thread if non-blocking, otherwise None.
        """
        from ..mission.executor import MissionExecutor
        executor = MissionExecutor(self)
        return executor.run(mission_or_action, blocking=blocking)

    def arm(self):
        """Arms the drone's motors via the connector."""
        self.connector.arm()

    def disarm(self):
        """Disarms the drone's motors via the connector."""
        self.connector.disarm()

    def set_mode(self, mode: str):
        """Sets the flight mode via the connector.

        Args:
            mode: The name of the mode to set (e.g., 'GUIDED', 'AUTO').
        """
        self.connector.set_mode(mode)

    def close(self):
        """Shuts down the drone connection and cleanup."""
        log.info("Closing drone connection...")
        self.connector.close()

    def __repr__(self):
        return f"Drone({self.connector.url}, {self.state})"
