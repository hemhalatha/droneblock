import threading
import time
from typing import Optional, TYPE_CHECKING
from pymavlink import mavutil
from ..core.connector import BaseConnector
from ..core.logger import get_logger
from ..core.exceptions import ConnectionError

if TYPE_CHECKING:
    from ..core.events import EventEmitter

log = get_logger("connectors.pymavlink")

class PymavlinkConnector(BaseConnector):
    """Pymavlink-based backend for DroneBlock.

    Adapts the synchronous pymavlink library to DroneBlock's event-driven 
    architecture using a dedicated background receiver thread.
    """

    def __init__(self, connection_url: str, events: 'EventEmitter') -> None:
        """Initializes the Pymavlink connector.

        Args:
            connection_url: Connection string (e.g., 'udp:127.0.0.1:14550').
            events: Shared EventEmitter instance.
        """
        super().__init__(connection_url, events)
        self.mav: Optional[Any] = None
        self._running: bool = False
        self._thread: Optional[threading.Thread] = None
        self.target_system: int = 1
        self.target_component: int = 1

    def connect(self) -> None:
        """Establishes MAVLink connection and starts the heartbeat monitor.

        Raises:
            ConnectionError: If no heartbeat is received within 10 seconds.
        """
        log.info(f"Opening MAVLink connection at {self.url}")
        self.mav = mavutil.mavlink_connection(self.url)
        
        # Wait for heartbeat to identify system IDs
        log.info("Waiting for vehicle heartbeat...")
        msg = self.mav.wait_heartbeat(timeout=10)
        if not msg:
            raise ConnectionError(f"Failed to connect to vehicle at {self.url} (Heartbeat timeout)")
            
        self.target_system = self.mav.target_system
        self.target_component = self.mav.target_component
        
        self._running = True
        self._thread = threading.Thread(
            target=self._recv_loop, 
            daemon=True, 
            name="PymavlinkRecvThread"
        )
        self._thread.start()
        log.info(f"MAVLink connected. System ID: {self.target_system}, Component ID: {self.target_component}")

    def _recv_loop(self) -> None:
        """Background thread for receiving MAVLink messages."""
        while self._running:
            try:
                msg = self.mav.recv_msg()
                if msg:
                    # Emit both generic and type-specific events
                    self.events.emit("mav.message", msg)
                    self.events.emit(f"mav.{msg.get_type()}", msg)
            except Exception as e:
                log.error(f"MAVLink receive error: {e}")
            time.sleep(0.001)  # High-frequency loop for telemetry

    def send_command(self, command: int, **params: float) -> None:
        """Sends a MAV_CMD_LONG message to the vehicle.

        Args:
            command: The MAVLink command ID.
            **params: Keyword parameters p1-p7 (e.g., p7=10 for altitude).
        """
        # Map p1-p7 keyword args to the positional arguments of command_long_send
        p = [params.get(f'p{i}', 0.0) for i in range(1, 8)]
        
        self.mav.mav.command_long_send(
            self.target_system,
            self.target_component,
            command,
            0,  # confirmation
            *p
        )

    def arm(self) -> None:
        """Sends a command to arm the vehicle's motors."""
        self.send_command(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, p1=1)

    def disarm(self) -> None:
        """Sends a command to disarm the vehicle's motors."""
        self.send_command(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, p1=0)

    def set_mode(self, mode_name: str) -> None:
        """Changes the flight mode of the vehicle.

        Args:
            mode_name: The target mode name (e.g., 'GUIDED').
        """
        if mode_name not in self.mav.mode_mapping():
            log.warning(f"Requested mode '{mode_name}' is not supported by the vehicle.")
            return
            
        mode_id = self.mav.mode_mapping()[mode_name]
        self.mav.set_mode(mode_id)
        log.debug(f"Mode change sent: {mode_name} ({mode_id})")

    def close(self) -> None:
        """Closes the MAVLink connection and stops the receiver thread."""
        log.info("Shutting down Pymavlink connector...")
        self._running = False
        if self.mav:
            self.mav.close()
        if self._thread:
            self._thread.join(timeout=1.0)
