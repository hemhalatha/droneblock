"""
DroneBlock Telemetry Mapping Module.

Responsible for translating raw MAVLink data into standard DroneBlock state.
"""
from typing import Any, TYPE_CHECKING
from ..core.state import VehicleGpsPosition, VehicleAttitude, BatteryStatus, VehicleStatus

if TYPE_CHECKING:
    from ..core.events import EventEmitter
    from ..core.state import DroneState

class TelemetryMapper:
    """Translation engine for normalizing raw MAVLink data into the DroneBlock state.

    This class subscribes to raw backend messages (e.g., from Pymavlink) and
    maps them to standardized, unit-normalized dataclass topics stored in the
    DroneState. It also re-emits these normalized topics on the event bus.
    """

    def __init__(self, events: 'EventEmitter', state: 'DroneState') -> None:
        """Initializes the mapper.

        Args:
            events: The event bus to listen for raw messages and emit normalized ones.
            state: The DroneState instance to update.
        """
        self.events = events
        self.state = state
        self._setup_subscriptions()

    def _setup_subscriptions(self) -> None:
        """Registers handlers for relevant raw MAVLink message types."""
        self.events.on("mav.GLOBAL_POSITION_INT", self._handle_gps)
        self.events.on("mav.ATTITUDE", self._handle_attitude)
        self.events.on("mav.SYS_STATUS", self._handle_battery)
        self.events.on("mav.HEARTBEAT", self._handle_heartbeat)

    def _handle_gps(self, msg: Any) -> None:
        """Normalizes GPS position and velocity data."""
        topic = VehicleGpsPosition(
            lat=msg.lat / 1e7,
            lon=msg.lon / 1e7,
            alt_msl=msg.alt / 1000.0,
            alt_rel=msg.relative_alt / 1000.0,
            vel_n_m_s=msg.vx / 100.0,
            vel_e_m_s=msg.vy / 100.0,
            vel_d_m_s=msg.vz / 100.0
        )
        self.state.update_topic("vehicle_gps_position", topic)
        self.events.emit("vehicle_gps_position", topic)

    def _handle_attitude(self, msg: Any) -> None:
        """Normalizes vehicle attitude (Euler angles)."""
        topic = VehicleAttitude(
            roll=msg.roll,
            pitch=msg.pitch,
            yaw=msg.yaw
        )
        self.state.update_topic("vehicle_attitude", topic)
        self.events.emit("vehicle_attitude", topic)

    def _handle_battery(self, msg: Any) -> None:
        """Normalizes battery voltage and remaining energy."""
        topic = BatteryStatus(
            voltage_v=msg.voltage_battery / 1000.0,
            remaining_pct=msg.battery_remaining
        )
        self.state.update_topic("battery_status", topic)
        self.events.emit("battery_status", topic)

    def _handle_heartbeat(self, msg: Any) -> None:
        """Normalizes basic vehicle status and connectivity data."""
        # Simple bitmask check for arming status
        armed = bool(msg.base_mode & 128) # MAV_MODE_FLAG_SAFETY_ARMED
        topic = VehicleStatus(
            armed=armed,
            nav_state="N/A" # Reserved for future mode-to-nav-state mapping
        )
        self.state.update_topic("vehicle_status", topic)
        self.events.emit("vehicle_status", topic)
